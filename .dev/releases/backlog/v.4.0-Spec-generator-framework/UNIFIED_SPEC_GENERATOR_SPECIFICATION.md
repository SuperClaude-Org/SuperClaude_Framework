# Unified Spec Generator Specification

> **Version**: 2.4.0 | **Status**: DRAFT | **Date**: 2026-01-22
> **Sources**: BMAD-METHOD, Clavix, Kiro, Shape Up, Amazon, Google, IEEE/ISO, AI-Native Research
> **Enhancement**: Brownfield Development Support (BF-01 through BF-09)

### Changelog

| Version | Date | Changes |
|---------|------|---------|
| **2.4.0** | 2026-01-22 | Adversarial Validation Engine (SpecDebateEngine) with conditional debates at Assumption Validation (Phase 2) and Pattern Conformance (BF-07), performance guardrails, mandatory debate outputs (traced findings + test stubs), user control flags (--debate-depth, --debate-focus) |
| **2.3.0** | 2026-01-22 | Risk-adjusted quality thresholds (tiered system replacing additive modifiers), question batching system with progress indicators, enhanced --prior-art-depth quick mode (README-only), requirements traceability model (Section 5.7), operability weight rebalanced (5%→8%, 10% for brownfield critical), canonical examples (Appendix C) |
| 2.2.0 | 2026-01-21 | Prior art discovery (BF-09), agent onboarding (BF-08), caching architecture |
| 2.1.0 | 2026-01-20 | Pattern conformance gate, history artifacts, quality threshold adjustments |
| 2.0.0 | 2026-01-19 | Brownfield development support (BF-01 through BF-07) |
| 1.0.0 | 2026-01-18 | Initial unified specification from 7+ framework synthesis |

---

## Executive Summary

This specification defines a comprehensive spec generator framework synthesizing best practices from 7+ primary sources and 100+ research files. The framework provides:

- **3-Phase Question Framework**: Discovery → Validation → Completion
- **3-Track Complexity Routing**: Quick (< 2 days) | Standard (2d-2w) | Enterprise (> 2w)
- **4-Layer Template Architecture**: Components → Composites → Tracks → Customization
- **8-Dimension Quality Scoring**: Weighted validation system with 80% threshold
- **AI-Native Optimization**: EARS notation, context blocks, structured schemas
- **Brownfield Development Support**: Agent onboarding, impact analysis, backwards compatibility, pattern conformance
- **Adversarial Validation Engine**: SpecDebateEngine with conditional debates at critical decision points

---

## Table of Contents

1. [Core Architecture](#1-core-architecture)
2. [Brownfield Context Acquisition](#2-brownfield-context-acquisition)
3. [External Prior Art Discovery](#3-external-prior-art-discovery) *(NEW - BF-09)*
4. [Question Framework](#4-question-framework)
5. [Complexity Routing](#5-complexity-routing)
6. [Template System](#6-template-system)
7. [Quality Validation](#7-quality-validation)
8. [Adversarial Validation Engine](#8-adversarial-validation-engine) *(NEW - v2.4)*
9. [AI Optimization](#9-ai-optimization)
10. [Workflow Process](#10-workflow-process)
11. [Tool Integration](#11-tool-integration)
12. [Development History Artifacts](#12-development-history-artifacts)
13. [Command Specification](#13-command-specification)
14. [Gap Analysis](#14-gap-analysis)

---

## 1. Core Architecture

### 1.1 System Overview

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                      SPEC GENERATOR ARCHITECTURE v2                                │
├───────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐      │
│  │   INPUT     │───▶│  COMPLEXITY  │───▶│  QUESTION   │───▶│   TEMPLATE   │      │
│  │   PROMPT    │    │   ROUTER     │    │  FRAMEWORK  │    │   ENGINE     │      │
│  └─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘      │
│         │                 │  ▲                │  ▲                │               │
│         │                 │  │                │  │                │               │
│         │                 │  │ ┌──────────────┴──┴────────────┐  │               │
│         │                 │  │ │    FEEDBACK CONTROLLER       │  │               │
│         │                 │  └─┤                               │  │               │
│         │                 │    │  REROUTE: complexity changed  │◀─┘               │
│         │                 │    │  GAP-FILL: validation gaps    │                  │
│  RESTART│                 │    │  CHECKPOINT: save progress    │                  │
│  (user) │                 │    └───────────────────────────────┘                  │
│         │                 ▼                                                       │
│         │           ┌──────────────┐    ┌─────────────┐    ┌──────────────┐      │
│         │           │   TRACK      │    │  ELICITED   │    │   RENDERED   │      │
│         │           │  SELECTION   │    │  ANSWERS    │    │     SPEC     │      │
│         │           └──────────────┘    └─────────────┘    └──────────────┘      │
│         │                                                         │               │
│         │                                                         ▼               │
│         │                                    ┌─────────────────────────────┐     │
│         │                                    │       VALIDATION            │     │
│         │                                    │  ┌─────────────────────────┐│     │
│         │                                    │  │ Score < 80%?            ││     │
│         │                                    │  │ ├─ Iteration < 3? → GAP ││     │
│         │                                    │  │ └─ Else → USER ESCAPE   ││     │
│         │                                    │  └─────────────────────────┘│     │
│         │                                    └─────────────────────────────┘     │
│         │                                                    │                    │
│         │                                        ┌───────────┴───────────┐       │
│         │                                        │                       │       │
│         │                              ≥80%      ▼            <80%       ▼       │
│         │                              ┌──────────────┐    ┌──────────────┐      │
│         └─────────────────────────────▶│    OUTPUT    │    │ USER ESCAPE  │      │
│                                        │ + AI Context │    │ OPTIONS      │      │
│                                        └──────────────┘    └──────────────┘      │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
```

**Feedback Loop Triggers**:

| Trigger | Condition | Action |
|---------|-----------|--------|
| **REROUTE** | Elicited answers change complexity by >15 points | Return to COMPLEXITY ROUTER |
| **GAP-FILL** | Validation finds missing information | Return to QUESTION FRAMEWORK |
| **CHECKPOINT** | Phase boundary or 5-minute interval | Save state to `.spec-generator/checkpoints/` |
| **RESTART** | User requests fresh start | Return to INPUT (optionally preserve context) |

### 1.2 Design Principles

| Principle | Source | Implementation |
|-----------|--------|----------------|
| **Problem-First** | All 7 sources | Always elicit problem before solution |
| **Scope Clarity** | Google, Shape Up | Explicit goals AND non-goals/exclusions |
| **Testable Output** | Kiro, IEEE | EARS notation → verifiable requirements |
| **Scale Awareness** | BMAD, Shape Up | Match process depth to complexity |
| **AI-Native** | Research | Structured schemas, context blocks |
| **Iterative** | All sources | Support refinement, not one-shot |

### 1.3 Key Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| Question Relevance | < 10% skip rate | Users shouldn't skip questions |
| Coverage Completeness | < 5% post-spec gaps | Requirements captured upfront |
| Time Efficiency | ≤ 80% of baseline | Faster than manual spec writing |
| User Satisfaction | ≥ 4/5 | Positive experience |
| Quality Score | ≥ 80% | Meets validation threshold |

---

## 2. Brownfield Context Acquisition

> **BF-01, BF-02, BF-08**: Mandatory pre-routing stage for brownfield projects

### 2.0 Agent Onboarding Check (BF-08)

> **BF-08**: Handle fresh agents encountering brownfield projects for the first time

When an agent encounters a brownfield project, it may be:
- **Fresh**: First time on this project (no Serena memories exist)
- **Stale**: Returning after extended absence (memories may be outdated)
- **Current**: Recently active on project (memories are valid)

This stage ensures agents have foundational project knowledge **before** attempting brownfield context acquisition.

#### 2.0.1 Agent State Detection

```yaml
agent_onboarding_check:
  position: "FIRST step in brownfield flow"
  trigger: "brownfield_mode activated"

  detection:
    step_1:
      tool: "mcp__serena__list_memories"
      purpose: "Check for existing project memories"

    step_2:
      evaluate:
        - exists: "onboarding_complete.md"
        - exists: "project_architecture.md"
        - exists: "project_conventions.md"
        - exists: "critical_paths.md"

    step_3:
      classify_state:
        fresh:
          condition: "No project-specific memories exist"
          action: "EXECUTE full bootstrap workflow"
        stale:
          condition: "Memories exist but age > stale_threshold OR significant_changes_detected"
          action: "EXECUTE reconciliation workflow"
        current:
          condition: "Recent valid memories exist"
          action: "SKIP to brownfield context acquisition"

  configuration:
    stale_threshold_days: 30
    significant_changes_threshold: 50  # commits since last memory update
```

#### 2.0.2 Bootstrap Workflow (Fresh Agent)

When an agent is fresh to a brownfield project, execute comprehensive knowledge acquisition:

```yaml
bootstrap_workflow:
  trigger: "agent_state == 'fresh'"
  estimated_duration: "2-5 minutes"
  parallel_execution: true

  stages:
    stage_1_architecture_discovery:
      name: "Architecture Discovery"
      tools: ["mcp__auggie-mcp__codebase-retrieval"]
      parallel_group: "A"

      queries:
        - information_request: "Main entry points, application architecture, and system organization"
        - information_request: "Core domain models, entities, and data structures"
        - information_request: "Service layer organization and dependency injection patterns"
        - information_request: "API structure and routing patterns"

      output:
        tool: "mcp__serena__write_memory"
        memory_file_name: "project_architecture.md"
        content_template: |
          # Project Architecture

          ## Overview
          {{architecture_summary}}

          ## Entry Points
          {{entry_points}}

          ## Domain Models
          {{domain_models}}

          ## Service Organization
          {{service_layer}}

          ## Last Updated
          {{timestamp}}

    stage_2_convention_extraction:
      name: "Convention Extraction"
      tools: ["Glob", "Read", "mcp__serena__find_symbol"]
      parallel_group: "A"

      analyze:
        naming_conventions:
          - file_patterns: "Glob('**/*.{ts,js,py}')"
          - extract: "naming style (camelCase, snake_case, PascalCase)"
          - sample_size: 20

        directory_structure:
          - tool: "mcp__serena__list_dir"
          - parameters: {relative_path: ".", recursive: false}
          - extract: "top-level organization pattern"

        import_patterns:
          - grep: "^import|^from|^require"
          - extract: "import organization style"

        error_handling:
          - auggie_query: "Error handling patterns and exception management"
          - extract: "try/catch patterns, error types, logging conventions"

      output:
        tool: "mcp__serena__write_memory"
        memory_file_name: "project_conventions.md"
        content_template: |
          # Project Conventions

          ## Naming Conventions
          - Files: {{file_naming}}
          - Functions: {{function_naming}}
          - Classes: {{class_naming}}
          - Variables: {{variable_naming}}

          ## Directory Structure
          {{directory_pattern}}

          ## Import Organization
          {{import_style}}

          ## Error Handling
          {{error_patterns}}

          ## Last Updated
          {{timestamp}}

    stage_3_history_capture:
      name: "Development History Capture"
      tools: ["Bash", "Read"]
      parallel_group: "B"

      capture:
        recent_commits:
          command: "git log --oneline -50"
          extract: "Recent development focus and patterns"

        major_versions:
          command: "git tag --sort=-version:refname | head -10"
          extract: "Version history and release cadence"

        readme_summary:
          file: "README.md"
          extract: "Project purpose, setup, key features"

        changelog:
          files: ["CHANGELOG.md", "HISTORY.md", "CHANGES.md"]
          extract: "Known changes and breaking changes history"

        tech_debt:
          grep_patterns: ["TODO:", "FIXME:", "HACK:", "XXX:"]
          extract: "Known technical debt locations"

      output:
        tool: "mcp__serena__write_memory"
        memory_file_name: "project_history.md"
        content_template: |
          # Project History

          ## Project Purpose
          {{readme_summary}}

          ## Recent Development Focus
          {{recent_commits_analysis}}

          ## Version History
          {{version_summary}}

          ## Known Technical Debt
          {{tech_debt_summary}}

          ## Last Updated
          {{timestamp}}

    stage_4_test_mapping:
      name: "Test Suite Mapping"
      tools: ["Glob", "mcp__auggie-mcp__codebase-retrieval"]
      parallel_group: "B"

      discover:
        test_directories:
          patterns: ["**/test/**", "**/tests/**", "**/__tests__/**", "**/spec/**"]

        test_file_patterns:
          patterns: ["*.test.*", "*.spec.*", "test_*.*", "*_test.*"]

        test_frameworks:
          detect: ["jest", "mocha", "pytest", "vitest", "playwright", "cypress"]
          source: "package.json, requirements.txt, config files"

        coverage_config:
          files: ["jest.config.*", "vitest.config.*", ".coveragerc", "pytest.ini"]

      output:
        tool: "mcp__serena__write_memory"
        memory_file_name: "test_mapping.md"
        content_template: |
          # Test Mapping

          ## Test Framework
          {{test_framework}}

          ## Test Directories
          {{test_directories}}

          ## Naming Patterns
          - Test files: {{test_file_pattern}}
          - Source → Test mapping: {{source_test_mapping}}

          ## Coverage Configuration
          {{coverage_config}}

          ## Last Updated
          {{timestamp}}

    stage_5_critical_path_identification:
      name: "Critical Path Identification"
      tools: ["mcp__auggie-mcp__codebase-retrieval", "Grep"]
      parallel_group: "C"

      identify:
        authentication:
          auggie_query: "Authentication, authorization, login, session management, JWT, OAuth"
          grep_patterns: ["auth", "login", "session", "token", "jwt"]
          risk_level: "critical"

        payment_processing:
          auggie_query: "Payment processing, transactions, billing, checkout, stripe, paypal"
          grep_patterns: ["payment", "checkout", "billing", "transaction"]
          risk_level: "critical"

        data_persistence:
          auggie_query: "Database operations, ORM, migrations, data models, repositories"
          grep_patterns: ["repository", "database", "migration", "model"]
          risk_level: "high"

        external_integrations:
          auggie_query: "External API integrations, third-party services, webhooks"
          grep_patterns: ["api", "webhook", "integration", "client"]
          risk_level: "high"

        security_sensitive:
          auggie_query: "Encryption, hashing, secrets, credentials, sensitive data handling"
          grep_patterns: ["encrypt", "hash", "secret", "credential", "sensitive"]
          risk_level: "critical"

      output:
        tool: "mcp__serena__write_memory"
        memory_file_name: "critical_paths.md"
        content_template: |
          # Critical Paths

          ## Authentication & Authorization
          - Files: {{auth_files}}
          - Risk Level: CRITICAL
          - Quality Modifier: +15%

          ## Payment Processing
          - Files: {{payment_files}}
          - Risk Level: CRITICAL
          - Quality Modifier: +15%

          ## Data Persistence
          - Files: {{data_files}}
          - Risk Level: HIGH
          - Quality Modifier: +10%

          ## External Integrations
          - Files: {{integration_files}}
          - Risk Level: HIGH
          - Quality Modifier: +10%

          ## Security Sensitive
          - Files: {{security_files}}
          - Risk Level: CRITICAL
          - Quality Modifier: +15%

          ## Last Updated
          {{timestamp}}

  completion:
    marker:
      tool: "mcp__serena__write_memory"
      memory_file_name: "onboarding_complete.md"
      content: |
        # Agent Onboarding Complete

        - Timestamp: {{timestamp}}
        - Bootstrap Version: 1.0
        - Memories Created:
          - project_architecture.md
          - project_conventions.md
          - project_history.md
          - test_mapping.md
          - critical_paths.md
        - Agent Ready: true
```

#### 2.0.3 Reconciliation Workflow (Stale Agent)

When an agent's memories are outdated, reconcile rather than rebuild:

```yaml
reconciliation_workflow:
  trigger: "agent_state == 'stale'"
  estimated_duration: "30-90 seconds"

  steps:
    step_1_detect_changes:
      name: "Detect Changes Since Last Update"
      tools: ["Bash"]

      commands:
        - "git log --oneline --since='{{last_memory_update}}'"
        - "git diff --stat {{last_memory_commit}}..HEAD"

      analysis:
        files_changed: "Extract list of modified files"
        areas_affected: "Categorize by architecture area"

    step_2_selective_update:
      name: "Selective Memory Update"

      rules:
        architecture_changed:
          condition: "Changes in entry points, core modules, or service layer"
          action: "Re-run stage_1_architecture_discovery"

        conventions_changed:
          condition: "New patterns introduced or lint config changed"
          action: "Re-run stage_2_convention_extraction"

        tests_changed:
          condition: "Test structure or framework changes"
          action: "Re-run stage_4_test_mapping"

        critical_paths_changed:
          condition: "Changes in auth, payment, or security areas"
          action: "Re-run stage_5_critical_path_identification"

    step_3_update_marker:
      tool: "mcp__serena__edit_memory"
      memory_file_name: "onboarding_complete.md"
      update: |
        - Last Reconciliation: {{timestamp}}
        - Changes Detected: {{change_summary}}
        - Memories Updated: {{updated_memories}}
```

#### 2.0.4 Command Options

```yaml
onboarding_command_options:
  --bootstrap:
    description: "Force full agent onboarding even if memories exist"
    use_case: "Reset agent knowledge after major refactoring"

  --skip-bootstrap:
    description: "Skip onboarding check entirely"
    use_case: "Quick spec generation when agent state is known"

  --bootstrap-depth:
    values: [quick, standard, deep]
    default: standard
    descriptions:
      quick: "Architecture + conventions only (30s)"
      standard: "All 5 stages (2-3 min)"
      deep: "Extended analysis with cross-referencing (5 min)"
```

### 2.1 Overview

For brownfield projects (extending existing codebases), understanding the impact of changes is essential **before** complexity routing can accurately assess the spec track. This stage:

- Discovers affected components using Auggie MCP semantic search
- Calculates impact radius (files, dependencies, tests affected)
- Captures performance baselines for regression detection
- Identifies critical paths requiring elevated quality thresholds

### 2.2 Activation Conditions

```yaml
brownfield_activation:
  indicators:
    - existing_project: true
    - feature_modifies_existing: true
    - auggie_returns_affected_components: ">0"

  skip_when:
    - greenfield_project: true
    - isolated_new_module: true
    - user_flag: "--skip-impact"
    - user_flag: "--greenfield"
```

### 2.3 Stage 0: Auggie Context Acquisition

**Purpose**: Enable semantic codebase understanding before spec generation.

```yaml
auggie_mcp_integration:
  position: "BEFORE complexity routing"
  mandatory: true

  steps:
    - name: "Domain Component Discovery"
      tool: "mcp__auggie-mcp__codebase-retrieval"
      parameters:
        information_request: "Components, classes, and functions related to {{feature_domain}}"
        directory_path: "{{project_root}}"
      output:
        variable: "affected_components"
        schema:
          files: ["path/to/file.ts"]
          symbols: ["ClassName", "functionName"]
          relationships: [{from: "A", to: "B", type: "imports"}]

    - name: "Pattern Extraction"
      tool: "mcp__auggie-mcp__codebase-retrieval"
      parameters:
        information_request: "Existing patterns, conventions, and architectural decisions in {{feature_domain}}"
        directory_path: "{{project_root}}"
      output:
        variable: "existing_patterns"

    - name: "Dependency Mapping"
      tool: "mcp__auggie-mcp__codebase-retrieval"
      parameters:
        information_request: "What depends on {{affected_components}} and what do they depend on?"
        directory_path: "{{project_root}}"
      output:
        variable: "dependency_graph"

  error_handling:
    auggie_unavailable:
      fallback: "Use Grep + Glob for file-based component discovery"
      warning: "⚠️ Semantic analysis unavailable - using file-based fallback"
      quality_impact: "-10% confidence in affected_components accuracy"
```

### 2.4 Stage 1: Impact Radius Calculation

```yaml
impact_radius_calculation:
  inputs:
    - auggie_affected_components
    - serena_project_context

  calculations:
    files_in_radius:
      formula: "count(affected_components.files)"
      thresholds:
        low: "1-5 files"
        medium: "6-15 files"
        high: "16+ files"

    dependency_depth:
      formula: "max_depth(dependency_graph)"
      thresholds:
        shallow: "1-2 levels"
        moderate: "3-4 levels"
        deep: "5+ levels"

    abstraction_touch_score:
      formula: |
        sum(
          base_class_modified * 3,
          interface_modified * 2,
          shared_utility_modified * 1.5,
          isolated_implementation * 1
        )
      interpretation: "Higher scores = more regression risk"

  output:
    impact_radius:
      files_count: "{{files_in_radius}}"
      dependency_depth: "{{dependency_depth}}"
      abstraction_score: "{{abstraction_touch_score}}"
      risk_level: "low|medium|high|critical"
```

### 2.5 Stage 2: Baseline Capture

**Purpose**: Establish metrics to detect regressions after implementation.

```yaml
baseline_capture:
  performance_baselines:
    - metric: "response_time_p50"
      for_endpoints: "{{affected_endpoints}}"
    - metric: "response_time_p95"
      for_endpoints: "{{affected_endpoints}}"
    - metric: "memory_baseline"
      for_components: "{{affected_components}}"

  quality_baselines:
    - metric: "test_pass_rate"
      required: "100% for affected suites"
    - metric: "test_coverage"
      for_files: "{{affected_files}}"
    - metric: "lint_errors"
      for_files: "{{affected_files}}"

  complexity_baselines:
    - metric: "cyclomatic_complexity"
      for_functions: "{{affected_functions}}"
    - metric: "cognitive_complexity"
      for_functions: "{{affected_functions}}"

  output:
    baseline_metrics:
      performance: "{{performance_baselines}}"
      quality: "{{quality_baselines}}"
      complexity: "{{complexity_baselines}}"
      captured_at: "{{ISO_8601}}"
```

### 2.6 Stage 3: Regression Test Mapping

```yaml
regression_test_discovery:
  methods:
    - file_mapping: "src/foo.ts → test/foo.test.ts"
    - auggie_query: "Test files that cover {{affected_components}}"
    - serena_memory: "read_memory('test_mapping')"

  output:
    required_test_suites:
      - suite: "{{test_file}}"
        covers: ["{{component1}}", "{{component2}}"]
        must_pass: true

    regression_test_plan:
      unit_tests: ["{{list}}"]
      integration_tests: ["{{list}}"]
      e2e_tests: ["{{list}}"]
      manual_tests: ["{{list if any}}"]
```

### 2.7 Stage 4: Critical Path Detection

```yaml
critical_path_detection:
  indicators:
    authentication_flow: "+15% quality threshold"
    payment_processing: "+15% quality threshold"
    data_persistence: "+10% quality threshold"
    user_facing_api: "+10% quality threshold"
    shared_abstraction: "+10% quality threshold"
    high_traffic_endpoint: "+5% quality threshold"

  output:
    critical_paths:
      - path: "{{path_description}}"
        indicator: "{{matched_indicator}}"
        quality_modifier: "+{{X}}%"

    adjusted_quality_threshold:
      base: 80
      modifier: "{{sum of quality_modifiers}}"
      final: "{{base + modifier, capped at 115}}"
```

### 2.8 Output Artifact

```yaml
impact_analysis.json:
  location: ".spec-generator/analysis/"
  contents:
    impact_radius: "{{stage_1_output}}"
    baseline_metrics: "{{stage_2_output}}"
    regression_tests: "{{stage_3_output}}"
    critical_paths: "{{stage_4_output}}"
    generated_at: "{{ISO_8601}}"

  used_by:
    - complexity_routing: "impact_radius feeds scoring"
    - question_framework: "auto-populates BF questions"
    - template_rendering: "injects into Backwards Compatibility"
    - quality_validation: "uses adjusted thresholds"
```

---

## 3. External Prior Art Discovery

> **BF-09**: Mandatory research stage to prevent reinventing the wheel by learning from existing solutions

### 3.1 Overview

Before generating a specification, the system searches GitHub for existing projects with similar objectives, analyzes their approaches, and critically evaluates their applicability. This ensures:

- **Learning from existing solutions**: Don't rebuild what's already been solved well
- **Pattern discovery**: Identify proven patterns and anti-patterns
- **Informed decisions**: Make architectural choices with full awareness of alternatives
- **Quality benchmarking**: Understand what "good" looks like in this domain

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      PRIOR ART RESEARCH WORKFLOW                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  1. DISCOVERY          2. SCORING           3. SHALLOW SCAN                    │
│  ┌───────────┐         ┌───────────┐        ┌───────────┐                      │
│  │ GitHub    │────────▶│ Trust +   │───────▶│ Directory │                      │
│  │ Search    │         │ Relevance │        │ Analysis  │                      │
│  │           │         │ Score     │        │           │                      │
│  │ 10-15     │         │           │        │ Find      │                      │
│  │ candidates│         │ Rank &    │        │ Relevant  │                      │
│  └───────────┘         │ Filter    │        │ Files     │                      │
│       │                └───────────┘        └───────────┘                      │
│       │                     │                    │                              │
│       ▼                     ▼                    ▼                              │
│  Feature keywords      Top 3-5 repos       File relevance                      │
│  + domain + lang       (score > 40)        map per repo                        │
│                                                  │                              │
│  4. DEEP DIVE          5. DEBATE            6. INFLUENCE                       │
│  ┌───────────┐         ┌───────────┐        ┌───────────┐                      │
│  │ Auggie    │────────▶│ Spec      │───────▶│ Tiered    │                      │
│  │ Analysis  │         │ Panel     │        │ Adoption  │                      │
│  │           │         │ Review    │        │           │                      │
│  │ Relevant  │         │           │        │ 80+: Strong│                     │
│  │ files only│         │ Merits?   │        │ 60-79: Mod │                     │
│  │           │         │ Flaws?    │        │ 40-59: Ref │                     │
│  └───────────┘         └───────────┘        └───────────┘                      │
│       │                     │                    │                              │
│       ▼                     ▼                    ▼                              │
│  Pattern extraction    Cross-repo           Spec integration                   │
│  + lessons learned     synthesis            decisions                          │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Stage 1: GitHub Discovery

```yaml
github_discovery:
  trigger: "MANDATORY for all specs"
  position: "After brownfield context (if applicable), before complexity routing"

  search_construction:
    primary_query:
      template: "{{feature_keywords}} language:{{project_language}}"
      filters:
        - "stars:>100"           # Minimum credibility threshold
        - "pushed:>2024-01-01"   # Active maintenance
      sort: "stars"
      max_results: 15

    fallback_queries:
      - "{{domain_keywords}} {{framework}}"        # Broader domain search
      - "{{problem_description}} example"          # Tutorial/example repos
      - "{{feature_type}} library {{language}}"    # Library implementations

  tools:
    primary: "Bash: gh search repos"
    fallback: "WebSearch: site:github.com"

  example:
    feature: "OAuth2 authentication with Google"
    language: "typescript"
    generated_query: "oauth2 google authentication language:typescript stars:>100 pushed:>2024-01-01"

  output:
    candidates:
      - repo: "nextauthjs/next-auth"
        stars: 22000
        description: "Authentication for Next.js"
        last_push: "2026-01-20"
      - repo: "passport/passport"
        stars: 22500
        description: "Simple, unobtrusive authentication for Node.js"
        last_push: "2026-01-15"
      # ... up to 15 candidates
```

### 3.3 Stage 2: Trust & Relevance Scoring

```yaml
scoring_algorithm:
  trust_score:  # 0-100: "Is this repo high quality?"
    components:
      github_signals:
        stars:
          weight: 0.20
          scale:
            "100-500": 20
            "500-2000": 40
            "2000-10000": 60
            "10000-50000": 80
            ">50000": 95

        maintenance:
          weight: 0.25
          factors:
            last_commit_recency:
              "<1 month": 100
              "1-3 months": 80
              "3-6 months": 60
              "6-12 months": 40
              ">12 months": 10
            has_recent_release: "+15"
            issues_response_rate: "% with maintainer response"

        community:
          weight: 0.15
          factors:
            contributors: "log10(count) * 20, cap 100"
            forks: "log10(count) * 15, cap 100"

      code_quality:
        weight: 0.25
        signals:
          has_tests: "+25 if test/ or __tests__/ exists"
          has_ci: "+20 if .github/workflows/ exists"
          has_typescript: "+15 if TypeScript"
          documentation: "+15 if comprehensive README"

      adoption:
        weight: 0.15
        signals:
          dependents: "GitHub dependents count"
          npm_weekly: "npm weekly downloads (if applicable)"

  relevance_score:  # 0-100: "Does this solve our problem?"
    components:
      problem_match:
        weight: 0.40
        method: "Semantic similarity: feature_description ↔ repo_description"
        tool: "Auggie semantic comparison OR keyword overlap %"

      feature_overlap:
        weight: 0.35
        method: "% of our required capabilities that repo implements"
        detection: "README parsing + directory structure analysis"

      architecture_fit:
        weight: 0.25
        method: "Pattern compatibility assessment"
        factors:
          - "Same architectural style (monolith/microservice/serverless)"
          - "Compatible dependency approach"
          - "Similar scale assumptions"

  applicability_score:  # 0-100: "Can we actually use this?"
    components:
      tech_stack_match:
        weight: 0.40
        factors:
          same_language: "+40"
          same_framework: "+30"
          compatible_runtime: "+20"
          different_but_portable: "+10"

      scale_match:
        weight: 0.30
        assessment: "Repo's target scale vs our requirements"

      complexity_match:
        weight: 0.30
        assessment: "Over-engineered? Under-engineered? Just right?"

  composite_influence_score:
    formula: "(trust × 0.30) + (relevance × 0.40) + (applicability × 0.30)"
    rationale: "Relevance weighted highest - a relevant mediocre repo beats an excellent irrelevant one"
```

### 3.4 Stage 3: Shallow Repository Scan

```yaml
shallow_scan:
  purpose: "Identify relevant files without cloning entire repo"
  duration: "10-30 seconds per repo"
  target: "All repos scoring > 40 on preliminary trust score"

  steps:
    step_1_structure_analysis:
      tool: "gh api /repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
      extract:
        - "Full directory tree"
        - "File paths and names"
        - "File extensions (tech stack confirmation)"
      output: "file_tree[]"

    step_2_readme_analysis:
      tool: "WebFetch: raw.githubusercontent.com/{owner}/{repo}/HEAD/README.md"
      extract:
        - "Feature descriptions"
        - "Architecture overview"
        - "Directory explanations"
        - "Key file references"
      output: "readme_insights{}"

    step_3_file_relevance_scoring:
      method: "Score each file's relevance to our feature"

      scoring_rules:
        keyword_in_filename:
          pattern: "filename contains {{feature_keyword}}"
          score: "+30"
          example: "auth" in "src/auth/oauth.ts"

        relevant_directory:
          pattern: "file in directory matching {{feature_domain}}"
          score: "+25"
          example: "src/authentication/*"

        mentioned_in_readme:
          pattern: "file referenced in README feature section"
          score: "+20"

        common_pattern_match:
          patterns: ["controller", "service", "handler", "middleware", "provider"]
          score: "+15"

        test_for_feature:
          pattern: "test file for relevant source file"
          score: "+10"

      threshold: 50
      max_files: 15

  output:
    per_repo:
      repo: "nextauthjs/next-auth"
      total_files: 847
      relevant_files:
        - path: "packages/core/src/lib/actions/callback/oauth/callback.ts"
          relevance: 95
          reason: "OAuth callback handling - core auth flow"
        - path: "packages/core/src/providers/google.ts"
          relevance: 90
          reason: "Google provider implementation"
        - path: "packages/core/src/lib/actions/session.ts"
          relevance: 75
          reason: "Session management"
      reduction: "847 → 12 files (98.6% reduction)"
```

### 3.5 Stage 4: Deep Dive Analysis

```yaml
deep_dive:
  purpose: "Semantic analysis of relevant files to extract patterns and lessons"
  target: "Top 3-5 repos by influence_score (threshold: 50+)"
  duration: "30-90 seconds per repo"

  method_selection:
    primary: "Auggie Cloud (Augment Code's context engine)"
    fallback: "Direct file fetch + Claude analysis"

  workflow:
    step_1_clone:
      command: "git clone --depth 1 {repo_url} /tmp/prior-art/{repo_slug}/"
      purpose: "Enable Auggie indexing"
      cleanup: "Delete after analysis"

    step_2_auggie_indexing:
      tool: "mcp__auggie-mcp__codebase-retrieval"
      parameters:
        directory_path: "/tmp/prior-art/{repo_slug}/"
        information_request: "Index this codebase for semantic search"
      note: "Auggie cloud maintains index for future queries"

    step_3_targeted_queries:
      tool: "mcp__auggie-mcp__codebase-retrieval"
      queries:
        architecture:
          request: "How is {{feature_name}} architecturally organized in this codebase?"

        implementation:
          request: "Show me the core implementation of {{feature_name}}"
          focus_files: "{{relevant_files}}"

        patterns:
          request: "What design patterns are used for {{feature_domain}}?"

        error_handling:
          request: "How does this codebase handle errors in {{feature_domain}}?"

        edge_cases:
          request: "What edge cases does {{feature_name}} handle?"

    step_4_extract_insights:
      per_repo:
        patterns_identified:
          - name: "Strategy pattern for OAuth providers"
            location: "src/providers/index.ts"
            description: "Pluggable provider architecture"

        lessons_learned:
          - insight: "Token refresh uses exponential backoff"
            applicability: "Adopt - prevents rate limiting"

        concerns_identified:
          - issue: "Tight coupling to specific session store"
            impact: "May limit our flexibility"

        code_snippets:
          - purpose: "Provider abstraction interface"
            code: |
              interface OAuthProvider {
                authorize(state: string): URL;
                callback(code: string): Promise<TokenSet>;
                refresh(token: string): Promise<TokenSet>;
              }

  output:
    analysis_report:
      repo: "nextauthjs/next-auth"
      influence_score: 82

      architecture_summary: |
        Next-Auth uses a layered architecture:
        - Providers layer: Pluggable OAuth/credentials providers
        - Actions layer: Core authentication flows (signin, callback, session)
        - Adapters layer: Database abstraction for session/user storage

      key_patterns:
        - pattern: "Provider Strategy"
          description: "Each OAuth provider implements common interface"
          recommendation: "ADOPT - excellent extensibility"

        - pattern: "Adapter Pattern for Storage"
          description: "Abstract database operations behind adapter interface"
          recommendation: "ADOPT - enables multiple storage backends"

      lessons:
        - "Separate token management from session management"
        - "Use PKCE for all OAuth flows, not just public clients"
        - "Implement token rotation by default"

      warnings:
        - "Complex callback URL handling may be over-engineered for simple cases"
        - "TypeScript types are extensive - good for safety, adds learning curve"
```

### 3.6 Stage 5: Comparative Spec-Panel Debate

```yaml
prior_art_debate:
  purpose: "Critical evaluation of each repo's approach through expert perspectives"
  method: "spec-panel-lite with focused experts"

  panel_composition:
    experts:
      - persona: "ARCHITECT"
        focus: "Architectural patterns, scalability, maintainability"

      - persona: "SECURITY"
        focus: "Security patterns, vulnerability potential"
        condition: "If feature involves auth, data, or external APIs"

      - persona: "REFACTORER"
        focus: "Code quality, technical debt potential, maintainability"

      - persona: "PERFORMANCE"
        focus: "Performance implications, scalability concerns"
        condition: "If feature is performance-sensitive"

  debate_structure:
    phase_1_individual_assessment:
      per_repo:
        - "What are the strengths of this approach?"
        - "What are the weaknesses or risks?"
        - "How applicable is this to our context?"
        - "What would we need to adapt?"

    phase_2_cross_repo_comparison:
      questions:
        - "How do these approaches differ fundamentally?"
        - "Which patterns appear across multiple repos (consensus)?"
        - "Where do repos disagree (trade-off indicator)?"
        - "What does no repo handle well (gap indicator)?"

    phase_3_synthesis:
      outputs:
        - "Recommended hybrid approach combining best elements"
        - "Patterns to definitely adopt"
        - "Patterns to definitely avoid"
        - "Open questions requiring further investigation"

  output:
    debate_summary:
      consensus_patterns:
        - pattern: "Provider abstraction"
          repos_using: ["next-auth", "passport", "auth0-spa-js"]
          recommendation: "ADOPT - industry consensus"

      divergent_approaches:
        - aspect: "Session storage"
          approaches:
            - repo: "next-auth"
              approach: "JWT + database hybrid"
              pros: "Stateless + persistence"
              cons: "Complexity"
            - repo: "passport"
              approach: "Server-side sessions only"
              pros: "Simple, secure"
              cons: "Requires sticky sessions"
          recommendation: "Choose based on infrastructure constraints"

      gaps_identified:
        - "No repo handles graceful degradation during provider outages well"
        - "Rate limiting on token refresh is inconsistent"

      synthesized_approach: |
        Recommend combining:
        - Provider abstraction from next-auth (extensibility)
        - Session serialization approach from passport (simplicity)
        - Error handling patterns from auth0-spa-js (user experience)
```

### 3.7 Stage 6: Influence Scoring & Spec Integration

```yaml
influence_tiers:
  tier_1_strong_adoption:
    score_range: "80-100"
    meaning: "High confidence - strongly recommend adopting patterns"

    spec_integration:
      prior_art_section: "Featured prominently with detailed analysis"
      solution_design: "Directly influences architectural decisions"
      implementation_notes: "Specific file/pattern references included"
      code_examples: "Include adapted code snippets"

    actions:
      - "Reference as primary inspiration in spec"
      - "Adopt key patterns with attribution"
      - "Link to specific implementation files"
      - "Include in 'Recommended Approach' section"

  tier_2_moderate_influence:
    score_range: "60-79"
    meaning: "Good reference - adopt selectively with adaptation"

    spec_integration:
      prior_art_section: "Listed with analysis and caveats"
      alternatives_considered: "Include as considered approach"
      lessons_learned: "Extract applicable insights"

    actions:
      - "Document in 'Alternatives Considered'"
      - "Extract specific patterns worth adopting"
      - "Note required adaptations for our context"
      - "Reference for specific sub-problems"

  tier_3_reference_only:
    score_range: "40-59"
    meaning: "Interesting but limited direct applicability"

    spec_integration:
      prior_art_section: "Brief mention with reason for limited adoption"
      notes: "Specific patterns worth noting"

    actions:
      - "Document in 'Evaluated Repositories'"
      - "Note why not fully applicable"
      - "Extract any isolated useful patterns"

  tier_4_excluded:
    score_range: "0-39"
    meaning: "Below threshold - not included in spec"

    actions:
      - "Log in research notes only"
      - "May inform what NOT to do"
      - "Not included in final spec"

dynamic_threshold_adjustment:
  excellent_options:
    condition: "3+ repos score above 75"
    action: "Raise tier_1 threshold to 85, be highly selective"

  limited_options:
    condition: "No repos score above 60"
    action: "Lower all thresholds by 10 points"
    rationale: "Some prior art better than none"

  one_standout:
    condition: "1 repo scores 20+ points above next best"
    action: "Feature standout prominently, briefly note others"

  minimum_viable:
    rule: "Always include at least 1 repo if any score >30"
    rationale: "Provide perspective even if imperfect match"
```

### 3.8 Caching Architecture

```yaml
caching_strategy:
  purpose: "Avoid redundant analysis of previously researched repositories"

  architecture:
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                        PRIOR ART CACHE LAYERS                           │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │  LAYER 1: Serena Local (Project-Specific)                              │
    │  ┌─────────────────────────────────────────────────────────────────┐   │
    │  │ memories/prior-art/                                              │   │
    │  │ ├── catalog.md           # Index of all analyzed repos          │   │
    │  │ ├── auth/                 # Domain-organized analyses           │   │
    │  │ │   ├── next-auth.md     # Full analysis summary               │   │
    │  │ │   ├── passport.md                                            │   │
    │  │ │   └── auth0-spa-js.md                                        │   │
    │  │ └── payment/                                                    │   │
    │  │     └── stripe-node.md                                         │   │
    │  └─────────────────────────────────────────────────────────────────┘   │
    │  Speed: <1 second | Storage: ~50KB per repo | Scope: This project     │
    │                                                                         │
    │  LAYER 2: Auggie Cloud (Cross-Project Semantic Index)                  │
    │  ┌─────────────────────────────────────────────────────────────────┐   │
    │  │ Augment Code's Context Engine                                    │   │
    │  │ ├── Maintains embeddings for cloned repos                       │   │
    │  │ ├── Semantic search across previously indexed codebases         │   │
    │  │ ├── Shared across all users of Auggie                          │   │
    │  │ └── Automatic re-indexing on repo updates                       │   │
    │  └─────────────────────────────────────────────────────────────────┘   │
    │  Speed: 2-5 seconds | Storage: Cloud | Scope: All Auggie users        │
    │                                                                         │
    │  LAYER 3: Centralized Prior Art Service (FUTURE)                       │
    │  ┌─────────────────────────────────────────────────────────────────┐   │
    │  │ Shared Vector Store / Knowledge Base                             │   │
    │  │ ├── Aggregated analyses from all users/projects                 │   │
    │  │ ├── Pre-indexed popular repos by domain                         │   │
    │  │ ├── Community-contributed insights and ratings                  │   │
    │  │ ├── Semantic search across all prior art                        │   │
    │  │ └── API: query(domain, feature_keywords) → ranked_analyses      │   │
    │  └─────────────────────────────────────────────────────────────────┘   │
    │  Speed: <500ms | Storage: Centralized | Scope: All users/projects     │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

  layer_1_serena_local:
    purpose: "Project-specific prior art memories"

    catalog_structure:
      tool: "mcp__serena__write_memory"
      file: "prior-art/catalog.md"
      content: |
        # Prior Art Catalog

        ## Indexed Repositories

        | Repo | Domain | Score | Last Analyzed | Status |
        |------|--------|-------|---------------|--------|
        | nextauthjs/next-auth | auth | 82 | 2026-01-22 | current |
        | passport/passport | auth | 75 | 2026-01-22 | current |

        ## Domain Index
        - auth: [next-auth, passport, auth0-spa-js]
        - payment: [stripe-node, square-connect]

    per_repo_memory:
      tool: "mcp__serena__write_memory"
      file: "prior-art/{domain}/{repo-slug}.md"
      content: |
        # Prior Art Analysis: {repo_name}

        ## Metadata
        - URL: {repo_url}
        - Stars: {stars}
        - Last Analyzed: {timestamp}
        - Trust Score: {trust_score}
        - Relevance Score: {relevance_score}
        - Influence Score: {influence_score}
        - Tier: {tier}

        ## Architecture Summary
        {architecture_summary}

        ## Key Patterns
        {patterns_list}

        ## Lessons Learned
        {lessons}

        ## Relevant Files
        {file_map}

        ## Code Snippets
        {snippets}

        ## Warnings/Concerns
        {warnings}

    ttl: "90 days before staleness check"
    refresh_trigger: "Repo has significant updates since last analysis"

  layer_2_auggie_cloud:
    purpose: "Semantic search across previously indexed repositories"

    workflow:
      on_analysis:
        1. "Clone repo to temp directory"
        2. "Auggie indexes codebase (embeddings stored in cloud)"
        3. "Delete local clone"
        4. "Auggie retains index for future semantic queries"

      on_cache_hit:
        1. "Query Auggie: 'How does {repo} implement {feature}?'"
        2. "Auggie searches its cloud index"
        3. "Returns relevant code snippets without re-cloning"

    benefits:
      - "No local storage required"
      - "Semantic search, not just keyword"
      - "Shared across Auggie user base"
      - "Automatic staleness detection"

  layer_3_future_centralized:
    purpose: "Community knowledge base of prior art analyses"

    vision:
      - "All Serena prior-art memories synced to central store"
      - "Vector embeddings enable semantic search"
      - "Query: 'Show me auth implementations using OAuth2 + Redis'"
      - "Returns: Ranked analyses from all users' research"
      - "Community ratings improve ranking over time"

    implementation_options:
      vector_stores:
        - "Pinecone"
        - "Weaviate"
        - "Qdrant"
        - "pgvector (PostgreSQL)"

      api_design:
        query_endpoint:
          input:
            domain: "auth"
            keywords: ["oauth2", "google", "session"]
            language: "typescript"
          output:
            - repo: "next-auth"
              score: 85
              analysis_summary: "..."
              contributor_count: 47  # How many users analyzed this

    timeline: "Phase 2 - After core spec generator is stable"

  cache_lookup_flow:
    ```
    Query: "OAuth2 with Google"

    1. Check Serena local → prior-art/catalog.md
       ├─ HIT: Read prior-art/auth/next-auth.md
       │       Return cached analysis
       │
       └─ MISS: Continue to Layer 2

    2. Check Auggie cloud index
       ├─ HIT: Query Auggie for cached semantic results
       │       Save summary to Serena local
       │       Return results
       │
       └─ MISS: Continue to fresh analysis

    3. Fresh analysis
       ├─ GitHub search → Clone → Auggie index → Analyze
       ├─ Save to Serena local (Layer 1)
       ├─ Auggie retains index (Layer 2)
       └─ Return results

    [FUTURE: Layer 3 query before fresh analysis]
    ```
```

### 3.9 Output Artifacts

```yaml
prior_art_artifacts:
  primary_output:
    location: "Embedded in spec document"
    sections:
      prior_art_summary:
        position: "After Problem Statement, before Solution Design"
        content:
          - "Repositories analyzed"
          - "Key patterns discovered"
          - "Lessons learned"
          - "Synthesized recommendation"

      alternatives_considered:
        position: "Standard spec section"
        enhanced_with:
          - "Prior art approaches as alternatives"
          - "Why adopted or not adopted"

  secondary_output:
    location: "specs/{feature}.prior-art.md"
    content:
      - "Full analysis for each repository"
      - "Debate transcript summary"
      - "Detailed code snippets"
      - "File relevance maps"

  cache_output:
    location: "Serena memory: prior-art/{domain}/{repo}.md"
    content:
      - "Reusable analysis for future specs"
      - "Domain-tagged for discovery"

spec_template_addition:
  section: "## Prior Art Research"

  template: |
    ## Prior Art Research

    ### Repositories Analyzed

    | Repository | Stars | Influence Score | Tier |
    |------------|-------|-----------------|------|
    {{#each prior_art_repos}}
    | [{{name}}]({{url}}) | {{stars}} | {{influence_score}} | {{tier}} |
    {{/each}}

    ### Key Patterns Discovered

    {{#each consensus_patterns}}
    #### {{name}}
    - **Found in**: {{repos_using}}
    - **Description**: {{description}}
    - **Recommendation**: {{recommendation}}
    {{/each}}

    ### Lessons Learned

    {{#each lessons}}
    - {{insight}} *(from {{source}})*
    {{/each}}

    ### Synthesized Approach

    {{synthesized_recommendation}}

    ### Warnings & Considerations

    {{#each warnings}}
    - ⚠️ {{warning}}
    {{/each}}
```

### 3.10 Command Options

```yaml
prior_art_options:
  --skip-prior-art:
    description: "Skip prior art research entirely"
    use_case: "When prior art already known or time-critical"
    warning: "Not recommended - may miss important patterns"

  --prior-art-depth:
    values: [quick, standard, deep]
    default: "standard"
    behaviors:
      quick:
        max_repos: 3
        analysis_scope: "readme_only"
        shallow_scan_only: true
        duration: "~30-60 seconds"
        description: |
          README-only analysis for rapid prior art assessment.
          - Fetches only README.md from top 3 repos
          - Extracts: purpose, key features, architecture summary
          - Skips: deep code analysis, spec-panel debate
          - Output: Brief summary of relevant prior art
        workflow:
          - step: "GitHub search"
            output: "Top 3 repos by relevance"
          - step: "README fetch"
            output: "README content for each repo"
          - step: "Quick extraction"
            extract: ["purpose", "key_features", "tech_stack", "notable_patterns"]
          - step: "Summary generation"
            output: "1-paragraph prior art summary"
        use_case: "Quick feature spec, internal tools, time-boxed exploration"
      standard:
        max_repos: 5
        analysis_scope: "full_6_stage"
        full_analysis: true
        duration: "~3-5 minutes"
        description: |
          Full 6-stage prior art analysis pipeline.
          - Complete shallow scan and deep dive
          - Spec-panel debate for critical evaluation
          - Influence scoring and adoption recommendations
      deep:
        max_repos: 8
        analysis_scope: "extended"
        extended_debate: true
        duration: "~8-10 minutes"
        description: |
          Extended analysis for complex/novel domains.
          - Additional repos and deeper analysis
          - Extended spec-panel debate with more experts
          - Comprehensive influence mapping

  --prior-art-domain:
    description: "Override auto-detected domain for search"
    example: "--prior-art-domain authentication"

  --prior-art-min-stars:
    description: "Minimum star threshold for repo consideration"
    default: 100
    example: "--prior-art-min-stars 1000"

  --force-prior-art-refresh:
    description: "Ignore cache, perform fresh analysis"
    use_case: "When cached analyses may be stale"
```

---

## 4. Question Framework

### 3.1 Three-Phase Approach

```
Phase 1: DISCOVERY (Broad → Specific)
   │
   ├── Amazon Five Questions
   ├── Shape Up Problem Story
   └── Clavix Socratic Flow
   │
   ▼
Phase 2: VALIDATION (Assumptions → Evidence)
   │
   ├── Backlog Research Taxonomy
   ├── BMAD Persona Questions
   └── Rabbit Holes Identification
   │
   ▼
Phase 3: COMPLETION (Gaps → Meta-review)
   │
   ├── Edge Case Questions
   ├── JTBD Validation
   └── EARS Formatting
```

### 3.1.1 Question Batching System

> **Purpose**: Reduce question fatigue by grouping related questions with clear progress indicators

**Problem Addressed**: Unbatched questions feel like interrogation. Users lose context switching between unrelated topics. Progress is unclear.

**Batching Strategy**:

```yaml
question_batching:
  overview: |
    Questions are grouped into themed batches with progress indicators.
    Each batch focuses on a coherent topic, reducing cognitive load.

  themed_batches:
    discovery_batches:
      - batch_id: "users_and_context"
        theme: "👤 Users & Context"
        questions: [Q1_primary_user, Q2_problem_story]
        progress_label: "Batch 1 of 3: Understanding your users"

      - batch_id: "goals_and_features"
        theme: "🎯 Goals & Features"
        questions: [Q3_success_criteria, Q4_key_features]
        progress_label: "Batch 2 of 3: Defining success"

      - batch_id: "scope_and_boundaries"
        theme: "📐 Scope & Boundaries"
        questions: [Q5_non_goals, Q6_constraints]
        progress_label: "Batch 3 of 3: Setting boundaries"

    validation_batches:
      - batch_id: "assumptions_check"
        theme: "🔍 Assumption Validation"
        questions: [probing_assumptions, probing_evidence]
        progress_label: "Validation 1 of 2: Checking assumptions"

      - batch_id: "perspectives_check"
        theme: "👥 Stakeholder Perspectives"
        questions: [viewpoint_questions, implications]
        progress_label: "Validation 2 of 2: Multiple viewpoints"

  track_question_caps:
    quick:
      max_questions: 6
      max_batches: 2
      skip_validation_phase: true
    standard:
      max_questions: 12
      max_batches: 4
      skip_validation_phase: false
    enterprise:
      max_questions: 18
      max_batches: 6
      require_all_phases: true

  progress_display:
    format: |
      ─────────────────────────────────────
      📋 {{batch_theme}}
         {{progress_label}}
         [{{current_batch}}/{{total_batches}}] {{progress_bar}}
      ─────────────────────────────────────

    example: |
      ─────────────────────────────────────
      📋 👤 Users & Context
         Batch 1 of 3: Understanding your users
         [1/3] ████░░░░░░ 33%
      ─────────────────────────────────────

  batch_transition:
    on_batch_complete: |
      ✅ {{batch_theme}} complete!
      Next: {{next_batch_theme}} ({{questions_remaining}} questions remaining)

      [Continue] [Skip to summary] [Go back]
```

**Benefits**:
- **Reduced cognitive load**: Related questions grouped together
- **Clear progress**: Users know where they are and how much remains
- **Natural breakpoints**: Users can pause between batches
- **Topic coherence**: Easier to maintain context within a theme

### 3.2 Phase 1: Discovery

**Objective**: Establish problem context and high-level requirements.

**Question Sequence** (Clavix + Amazon hybrid):

| Order | Question | Source | Format |
|-------|----------|--------|--------|
| 1 | Who is the primary user/customer? | Amazon Q1 | Open + Examples |
| 2 | What specific problem are they facing? | Amazon Q2, Shape Up | Story format |
| 3 | What does success look like? | Clavix Goal | Measurable criteria |
| 4 | What are the key features needed? | Clavix Features | Priority list |
| 5 | What is explicitly out of scope? | Google Non-goals | Exclusion list |

**Configuration**:
```yaml
discovery:
  max_questions_per_batch: 5
  confidence_threshold: 0.95
  default_behavior: "state_and_proceed"
  sequence: funnel  # broad → specific
```

### 3.3 Phase 2: Validation

**Objective**: Challenge assumptions and gather evidence.

**Question Taxonomy** (Backlog Research):

| Type | When to Use | Example |
|------|-------------|---------|
| Clarification | Ambiguous terms | "What do you mean by X?" |
| Probing Assumptions | Unstated beliefs | "What evidence supports X?" |
| Probing Evidence | Claims without data | "Where does this come from?" |
| Viewpoints | Single perspective | "How would ops team view this?" |
| Implications | Unclear impact | "If we do X, what happens to Y?" |
| Meta-questions | Completeness | "What haven't we discussed?" |

**Rabbit Holes Identification** (Shape Up):
```yaml
rabbit_holes:
  prompt: "What parts of this could become unexpectedly complex?"
  categories:
    - technical_unknowns
    - integration_challenges
    - edge_cases
    - scope_creep_risks
```

### 3.3.1 Non-Functional Requirements Elicitation

**Objective**: Capture quality attributes that constrain the solution.

**NFR Categories** (IEEE 25010 aligned):

| Category | Primary Question | Follow-up | Track Requirement |
|----------|------------------|-----------|-------------------|
| **Performance** | "What response time is acceptable?" | "What happens if threshold exceeded?" | Standard+ |
| **Reliability** | "What uptime is required?" | "What is the recovery procedure?" | Standard+ |
| **Scalability** | "How many concurrent users initially?" | "Expected growth over 12 months?" | When growth mentioned |
| **Maintainability** | "How will this be debugged?" | "What logging is needed?" | Enterprise |
| **Compatibility** | "What systems must this integrate with?" | "API versioning requirements?" | When integrations exist |

**Configuration**:
```yaml
nfr_elicitation:
  activation:
    tracks: [standard, enterprise]
    keywords: ["performance", "scale", "uptime", "load", "concurrent"]
    integration_points: "> 0"

  questions:
    performance:
      primary: "What response time is acceptable for the primary user action?"
      format: measurable
      default: "< 200ms for API calls"

    reliability:
      primary: "What is the acceptable downtime per month?"
      format: measurable
      default: "99.9% uptime (8.7 hours/year)"

    scalability:
      primary: "How many concurrent users must be supported?"
      format: numeric_range
      follow_up: "What growth rate over 12 months?"

    maintainability:
      primary: "What logging and debugging capabilities are required?"
      format: checklist
      options: ["structured_logs", "distributed_tracing", "metrics", "alerting"]

    compatibility:
      primary: "What external systems must this integrate with?"
      format: list
      follow_up: "What API versioning strategy is required?"
```

### 3.3.2 Brownfield Discovery Questions

> **BF-03**: Extend the Question Framework with brownfield-specific questions

**Activation**: When `brownfield_mode: true` AND `impact_analysis_completed: true`

**Question Bank**:

```yaml
brownfield_discovery_questions:
  bf_q1_interaction_mapping:
    id: "BF-Q1"
    question: "What existing features does this interact with?"
    format:
      type: "checklist_with_custom"
      auto_populate: true
      source: "impact_analysis.affected_components"
    confidence_impact: critical
    output_mapping:
      target_section: "Backwards Compatibility → Affected Components"

  bf_q2_test_requirements:
    id: "BF-Q2"
    question: "What test suites must pass for this to be considered complete?"
    format:
      type: "multi_select_grouped"
      auto_populate: true
      source: "impact_analysis.regression_tests"
      grouping: ["unit", "integration", "e2e", "manual"]
    validation:
      minimum_selection: 1
      warning_if_empty: "⚠️ No regression tests selected - high risk of undetected breaks"
    confidence_impact: critical
    output_mapping:
      target_section: "Backwards Compatibility → Regression Test Plan"

  bf_q3_performance_baselines:
    id: "BF-Q3"
    question: "What performance baselines must be maintained?"
    format:
      type: "table_input"
      auto_populate: true
      source: "impact_analysis.baseline_metrics.performance"
      columns:
        - name: "Endpoint/Component"
        - name: "Current p95"
        - name: "Acceptable Regression"
          options: ["0%", "5%", "10%", "20%", "Custom"]
    defaults:
      acceptable_regression: "10%"
    confidence_impact: high
    output_mapping:
      target_section: "NFR → Performance Constraints"

  bf_q4_deprecation_plan:
    id: "BF-Q4"
    question: "Does this feature replace or deprecate existing functionality?"
    format:
      type: "conditional_flow"
      initial: "yes_no"
      if_yes:
        follow_up_questions:
          - "What functionality is being replaced?"
          - "What is the migration path for existing users?"
          - "What is the deprecation timeline?"
        required_sections: ["Deprecation Plan", "Migration Guide"]
    confidence_impact: medium
    tracks: [standard, enterprise]
    output_mapping:
      target_section: "Backwards Compatibility → Deprecation Plan"

  bf_q5_rollback_strategy:
    id: "BF-Q5"
    question: "What is the rollback strategy if this feature causes issues?"
    format:
      type: "multiple_choice_with_custom"
      options:
        - label: "Feature flag (instant disable)"
          recommended_for: "High-risk changes"
        - label: "Database migration rollback"
          recommended_for: "Schema modifications"
        - label: "Git revert + deploy"
          recommended_for: "Code-only changes"
        - label: "Manual intervention required"
          warning: "⚠️ High-risk - consider feature flag"
    confidence_impact: high
    tracks: [standard, enterprise]
    output_mapping:
      target_section: "Risk Assessment → Rollback Strategy"
```

**Sequencing**:
```yaml
brownfield_question_flow:
  position: "After standard discovery Q1-Q5"
  sequence: [BF-Q1, BF-Q2, BF-Q3, BF-Q4, BF-Q5]

  skip_logic:
    quick_track:
      skip: [BF-Q4, BF-Q5]
      reason: "Quick track assumes low-risk isolated changes"
    isolated_module:
      skip: [BF-Q1, BF-Q2, BF-Q3]
      reason: "No existing functionality to preserve"
```

**Validation Phase Triggers**:
```yaml
brownfield_validation_triggers:
  - trigger: "abstraction_modification_detected"
    questions:
      - "How will existing code using {{abstraction}} handle the change?"
      - "Is the change backwards compatible?"

  - trigger: "critical_path_intersection"
    questions:
      - "What monitoring will detect issues in {{critical_path}}?"
      - "What is the blast radius if {{critical_path}} fails?"

  - trigger: "baseline_regression_risk > 10%"
    questions:
      - "Is the {{metric}} regression justified? What's the user impact?"
      - "Can we optimize to stay within baseline?"
```

### 3.4 Phase 3: Completion

**Objective**: Ensure requirements are complete and well-formed.

**Gap Analysis Questions**:
- "What happens when [edge case]?"
- "What error conditions haven't we addressed?"
- "What are the performance expectations?"

**JTBD Validation**:
- "Does this help the user accomplish their core job?"
- "What current solutions are being 'fired'?"

**Output Triggers**:
- EARS-formatted requirements
- Documented assumptions with confidence levels
- Identified risks and mitigation strategies

### 3.5 Adaptive Sequencing

| Context | Strategy | Start With |
|---------|----------|------------|
| New project, unclear scope | **Funnel** | Amazon Five Questions |
| Complex domain, multiple stakeholders | **Diamond** | Viewpoint questions |
| Iterative refinement | **Spiral** | Previous context review |
| Technical feasibility focus | **Tree** | Technical questions |

### 3.6 Response Adaptation (LSDE Metrics)

| Metric | Indicator | Adaptation |
|--------|-----------|------------|
| **Length** | Short responses | Probe deeper, offer examples |
| **Self-disclosure** | Low sharing | Build rapport, use story prompts |
| **Emotion** | Frustration detected | Acknowledge, simplify questions |
| **Specificity** | Vague answers | Request concrete examples |

---

## 5. Complexity Routing

### 4.1 Track Selection Matrix

| Criteria | Quick | Standard | Enterprise |
|----------|-------|----------|------------|
| **Scope** | Bug fix, spike, enhancement | Feature, integration, refactor | Strategic, compliance-critical |
| **Effort** | < 2 days | 2 days - 2 weeks | > 2 weeks |
| **Files** | 1-3 files | 4-15 files | > 15 files |
| **Stakeholders** | 1-2 | 3-5 | 5+ |
| **Review Level** | Informal | Standard | Formal sign-off |
| **Sections** | 5-8 | 10-12 | 15+ |

### 4.2 Auto-Detection Algorithm

```yaml
complexity_score:
  range: 0-100

  factors:
    effort_estimate:
      weight: 0.25
      scoring:
        "< 1 day": 10
        "1-2 days": 25
        "3-5 days": 40
        "1-2 weeks": 60
        "2-4 weeks": 80
        "> 1 month": 100

    file_count:
      weight: 0.20
      scoring:
        "1-3": 15
        "4-10": 40
        "11-15": 60
        "> 15": 85

    stakeholder_count:
      weight: 0.15
      scoring:
        "1-2": 20
        "3-5": 50
        "> 5": 80

    domain_complexity:
      weight: 0.20
      keywords:
        simple: ["bug", "fix", "typo", "update"]
        moderate: ["feature", "integrate", "refactor"]
        complex: ["architecture", "compliance", "migration", "security"]

    risk_level:
      weight: 0.20
      indicators:
        low: ["internal", "non-critical"]
        medium: ["customer-facing", "data"]
        high: ["security", "compliance", "production"]

  thresholds:
    # Confidence bands with overlap zones for user choice
    quick:
      core_range: [0, 25]
      transition_to_standard: [26, 35]
    standard:
      core_range: [36, 60]
      transition_to_enterprise: [61, 70]
    enterprise:
      core_range: [71, 100]

  routing_behavior:
    core_range: "auto_select"
    transition_zone: "present_both_options"

  transition_prompts:
    quick_standard: |
      Score {{SCORE}} is in the Quick/Standard transition zone.
      - Quick: Faster, 5-8 sections, best for simple changes
      - Standard: Comprehensive, 10-12 sections, better for features
      Which track fits your needs?

    standard_enterprise: |
      Score {{SCORE}} is in the Standard/Enterprise transition zone.
      - Standard: Feature-complete, 10-12 sections
      - Enterprise: Full compliance, 15+ sections, formal sign-off
      Which track fits your needs?

  override_capture:
    enabled: true
    fields: [selected_track, recommended_track, user_rationale]
```

### 4.3 Brownfield Impact Integration

> **BF-02**: Impact radius feeds into complexity scoring

```yaml
brownfield_scoring_adjustment:
  impact_radius_factor:
    weight: 0.20
    mapping:
      low: 0
      medium: 10
      high: 20
      critical: 30

  example:
    scenario: "Standard feature touching auth module"
    base_score: 45
    impact_radius: "high (+20)"
    final_score: 65
    result: "Transition zone → present Standard/Enterprise choice"
```

### 4.4 User Override

```yaml
override_options:
  - prompt: "Recommended track: Standard. Accept or choose different?"
  - choices:
    - label: "Accept Standard (Recommended)"
      value: standard
    - label: "Quick (simpler)"
      value: quick
      description: "Fewer sections, faster completion"
    - label: "Enterprise (more comprehensive)"
      value: enterprise
      description: "Full compliance, security, accessibility sections"
```

---

## 6. Template System

### 6.1 Four-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LAYER 4: CUSTOMIZATION                               │
│              .spec-generator/customize.yaml                             │
│              Project overrides, extensions, exclusions                  │
├─────────────────────────────────────────────────────────────────────────┤
│                    LAYER 3: TRACK TEMPLATES                             │
│              quick.md | standard.md | enterprise.md                     │
│              Complete specification templates by scope                  │
├─────────────────────────────────────────────────────────────────────────┤
│                    LAYER 2: COMPOSITES                                  │
│              Logical section groupings                                  │
│              goals-nongoals.md, requirements-block.md                   │
├─────────────────────────────────────────────────────────────────────────┤
│                    LAYER 1: CORE COMPONENTS                             │
│              Atomic building blocks                                     │
│              metadata/, sections/, fragments/, validations/             │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Track Templates

#### Quick Track (5-8 sections)

```markdown
{{INCLUDE:metadata/spec-header}}

# {{VAR:FEATURE_NAME}} Specification

## Problem Statement
{{INCLUDE:sections/problem-statement.minimal}}

## Solution Overview
{{INCLUDE:sections/solution-overview}}

## Scope
{{INCLUDE:sections/scope-in-out}}

## Success Criteria
{{INCLUDE:sections/success-criteria.minimal}}

{{CONDITIONAL:track=quick+risks}}
## Key Risks
{{INCLUDE:sections/risks.minimal}}
{{/CONDITIONAL}}

---
{{INCLUDE:ai-context/context-block}}
```

#### Standard Track (10-12 sections)

```markdown
{{INCLUDE:metadata/spec-header}}
{{INCLUDE:metadata/ownership}}

# {{VAR:FEATURE_NAME}} Specification

## Problem Statement
{{INCLUDE:sections/problem-statement}}

## Goals and Non-Goals
{{INCLUDE:sections/goals-nongoals}}

## Requirements
{{INCLUDE:sections/requirements.ears}}

## Solution Design
{{INCLUDE:sections/design}}

## Alternatives Considered
{{INCLUDE:sections/alternatives}}

## Risk Assessment
{{INCLUDE:sections/risks}}
{{INCLUDE:fragments/tables/risk-matrix}}

## Success Criteria
{{INCLUDE:sections/success-criteria}}

## Tasks and Milestones
{{INCLUDE:sections/tasks}}

## Open Questions
{{INCLUDE:sections/open-questions}}

---
{{INCLUDE:ai-context/context-block}}
```

#### Enterprise Track (15+ sections)

Includes all Standard sections plus:
- Executive Summary
- Compliance Requirements
- Security Review
- Accessibility Review
- Performance Requirements
- Monitoring and Observability
- Rollback Strategy
- Stakeholder Sign-off
- Audit Trail

### 5.3 Syntax Reference

| Syntax | Description | Example |
|--------|-------------|---------|
| `{{VAR:name}}` | Simple variable | `{{VAR:FEATURE_NAME}}` |
| `{{VAR:name\|default}}` | With default | `{{VAR:TRACK\|standard}}` |
| `{{VAR:name\|REQUIRED}}` | Required | `{{VAR:AUTHOR\|REQUIRED}}` |
| `{{INCLUDE:path}}` | Include component | `{{INCLUDE:sections/goals}}` |
| `{{INCLUDE:path.variant}}` | Include variant | `{{INCLUDE:sections/requirements.ears}}` |
| `{{CONDITIONAL:cond}}` | Conditional block | `{{CONDITIONAL:track=enterprise}}` |
| `{{FOREACH:items}}` | Loop | `{{FOREACH:requirements AS req}}` |

### 5.4 Customization

```yaml
# .spec-generator/customize.yaml
version: "1.0"

defaults:
  track: standard
  variables:
    PROJECT_NAME: "MyProject"
    TEAM: "Platform"

overrides:
  metadata/spec-header:
    source: custom/my-header.md

  sections/requirements:
    prepend: |
      > **Note**: All requirements follow RFC 2119.

tracks:
  enterprise:
    variables:
      REQUIRED_APPROVERS: ["Security", "Architecture"]
    insert_after:
      sections/compliance:
        - custom/regulatory-checklist
```

### 5.5 Template Versioning and Integrity

**Requirement**: Every template MUST include version metadata for reproducibility and integrity.

**Template Header Format**:
```yaml
---
template:
  id: "standard"
  version: "1.0.0"
  checksum: "sha256:a3f2b8c9..."
  last_modified: "2026-01-21"
  compatibility:
    spec_generator: ">=1.0.0"
  changelog:
    - version: "1.0.0"
      date: "2026-01-21"
      changes: ["Initial release"]
---
```

**Validation Pipeline**:
```
Load Template → Verify Checksum → Check Version → Check Compatibility → Accept/Reject
       │              │                │                 │
       ▼              ▼                ▼                 ▼
    [Parse]    [SHA256 match?]  [>= min version?]  [Breaking changes?]
                    │                  │                  │
                 NO ↓               NO ↓               YES ↓
              [REJECT]          [REJECT]         [WARN + suggest migrate]
```

**Spec-Template Linkage**:

Every generated spec includes template reference in metadata:
```yaml
spec_metadata:
  template:
    id: "standard"
    version: "1.0.0"
    checksum: "sha256:a3f2b8c9..."
  generator:
    version: "1.0.0"
    generated_at: "2026-01-21T14:30:00Z"
```

**Migration Support**:

When templates are updated with breaking changes:
```bash
# Check for affected specs
/sc:spec --check-migrations

# Migrate spec to new template version
/sc:spec @old-spec.md --migrate-template
```

### 5.6 Backwards Compatibility Components

> **BF-04**: Mandatory template sections for brownfield projects

**Purpose**: Every brownfield spec must explicitly document how existing functionality is preserved.

#### 5.6.1 Affected Components Table

```markdown
## Affected Components

> Auto-populated from impact analysis. Review and adjust as needed.

| Component | File Path | Impact Type | Regression Test |
|-----------|-----------|-------------|-----------------|
{{#each affected_components}}
| {{name}} | `{{path}}` | {{impact_type}} | {{test_suite}} |
{{/each}}

### Impact Legend
- **Modify**: Changing existing behavior
- **Extend**: Adding to existing component
- **Replace**: Superseding existing functionality
- **Depend**: New code depends on existing component
```

**Mandatory for**: Standard, Enterprise
**Optional for**: Quick

#### 5.6.2 Existing Behavior Preservation

```markdown
## Existing Behavior Preservation

> Document how current functionality continues to work after this change.

### Preserved Behaviors (EARS Format)

{{#each preserved_behaviors}}
**{{id}}**: WHEN [{{trigger}}] THE SYSTEM SHALL [{{current_behavior}}] SO THAT [{{user_value}}]

- **Verification**: {{verification_method}}
- **Test**: {{regression_test}}
{{/each}}

### Behavior Changes (If Any)

| Current Behavior | New Behavior | Justification | Migration |
|-----------------|--------------|---------------|-----------|
{{#each behavior_changes}}
| {{current}} | {{new}} | {{justification}} | {{migration_path}} |
{{/each}}
```

**Mandatory for**: Standard, Enterprise

#### 5.6.3 Performance Baselines Section

```markdown
## Performance Baselines

> Metrics captured before implementation. Regression thresholds must be maintained.

### Response Time Baselines

| Endpoint/Operation | Current p50 | Current p95 | Acceptable Regression | Threshold |
|-------------------|-------------|-------------|----------------------|-----------|
{{#each performance_baselines}}
| {{target}} | {{p50}}ms | {{p95}}ms | {{acceptable_regression}}% | {{threshold}}ms |
{{/each}}

### Regression Detection

- **Monitoring**: {{monitoring_approach}}
- **Alert Threshold**: {{alert_config}}
- **Rollback Trigger**: {{rollback_criteria}}
```

**Mandatory for**: Standard, Enterprise

#### 5.6.4 Regression Test Plan

```markdown
## Regression Test Plan

> Tests that must pass before this feature is considered complete.

### Automated Tests

#### Unit Tests
{{#each unit_tests}}
- [ ] `{{path}}` - {{description}}
{{/each}}

#### Integration Tests
{{#each integration_tests}}
- [ ] `{{path}}` - {{description}}
{{/each}}

#### E2E Tests
{{#each e2e_tests}}
- [ ] `{{path}}` - {{description}}
{{/each}}

### New Tests Required
{{#each new_tests_required}}
- [ ] **{{type}}**: {{description}}
  - **Covers**: {{coverage_target}}
  - **Priority**: {{priority}}
{{/each}}
```

**Mandatory for**: Quick, Standard, Enterprise (all tracks)

#### 5.6.5 Rollback Strategy

```markdown
## Rollback Strategy

> Plan for reverting this feature if issues are detected in production.

### Rollback Method

**Type**: {{rollback_type}}

{{#if feature_flag}}
#### Feature Flag Rollback
- **Flag Name**: `{{flag_name}}`
- **Disable Command**: `{{disable_command}}`
- **Time to Disable**: Instant
{{/if}}

{{#if database_rollback}}
#### Database Rollback
- **Down Migration**: `{{migration_file}}`
- **Data Preservation**: {{data_handling}}
- **Estimated Time**: {{rollback_time}}
{{/if}}

### Rollback Triggers

| Condition | Threshold | Action |
|-----------|-----------|--------|
{{#each rollback_triggers}}
| {{condition}} | {{threshold}} | {{action}} |
{{/each}}
```

**Mandatory for**: Standard, Enterprise
**Optional for**: Quick

#### 5.6.6 Composite Templates

```yaml
brownfield_composites:
  brownfield_standard:
    includes:
      - "bc-affected-components"
      - "bc-behavior-preservation"
      - "bc-performance-baselines"
      - "bc-regression-tests"
      - "bc-rollback"
      - "bc-deprecation"  # conditional
    position_in_spec: "After Requirements, Before Solution Design"

  brownfield_quick:
    includes:
      - "bc-regression-tests"
      - "bc-affected-components"  # optional
    position_in_spec: "After Problem Statement"

  brownfield_enterprise:
    includes:
      - "bc-affected-components"
      - "bc-behavior-preservation"
      - "bc-performance-baselines"
      - "bc-regression-tests"
      - "bc-rollback"
      - "bc-deprecation"
      - "bc-monitoring-integration"  # enterprise only
    position_in_spec: "Dedicated 'Backwards Compatibility' section"
```

### 5.7 Requirements Traceability Model

> **Purpose**: Enable bi-directional traceability between stakeholder needs, requirements, and verification

**Problem Addressed**: Requirements often lack clear connection to stakeholder needs (backward trace) and to tests/implementations (forward trace). This makes impact analysis difficult and reduces confidence in coverage.

**Traceability Schema**:

```yaml
requirements_traceability:
  overview: |
    Every requirement should trace backward to a stakeholder need and
    forward to its verification. This enables impact analysis, coverage
    verification, and change management.

  trace_model:
    backward_trace:
      description: "Connects requirement to originating stakeholder need"
      schema:
        requirement_id: "REQ-XXX"
        traces_to:
          stakeholder_need: "SN-XXX"
          need_description: "{{stakeholder_need_description}}"
          stakeholder: "{{stakeholder_role}}"
          priority: "{{MoSCoW_priority}}"
        rationale: "{{why_this_requirement_addresses_the_need}}"

    forward_trace:
      description: "Connects requirement to verification and implementation"
      schema:
        requirement_id: "REQ-XXX"
        verified_by:
          - type: "unit_test"
            test_id: "UT-XXX"
            test_path: "{{test_file_path}}"
          - type: "integration_test"
            test_id: "IT-XXX"
            test_path: "{{test_file_path}}"
          - type: "manual_verification"
            procedure: "{{verification_procedure}}"
        implemented_in:
          - file: "{{source_file}}"
            component: "{{component_name}}"
            lines: "{{line_range}}"

  trace_matrix_template: |
    ## Requirements Traceability Matrix

    | Req ID | Stakeholder Need | Requirement | Verified By | Implemented In |
    |--------|------------------|-------------|-------------|----------------|
    {{#each requirements}}
    | {{id}} | {{stakeholder_need}} | {{description}} | {{tests}} | {{implementation}} |
    {{/each}}

  coverage_metrics:
    backward_coverage: "% of requirements with stakeholder need trace"
    forward_coverage: "% of requirements with test trace"
    implementation_coverage: "% of requirements with implementation trace"
    minimum_thresholds:
      quick: "backward: 50%, forward: 80%"
      standard: "backward: 80%, forward: 90%"
      enterprise: "backward: 100%, forward: 100%"

  example:
    requirement:
      id: "REQ-AUTH-001"
      description: "WHEN user submits credentials THE SYSTEM SHALL validate against identity provider SO THAT only authenticated users access protected resources"
      backward_trace:
        stakeholder_need: "SN-SEC-001"
        need_description: "Prevent unauthorized access to customer data"
        stakeholder: "Security Team"
        priority: "MUST"
        rationale: "Authentication is the primary control against unauthorized access"
      forward_trace:
        verified_by:
          - type: "unit_test"
            test_id: "UT-AUTH-001"
            test_path: "tests/unit/auth/credentials.test.ts"
          - type: "integration_test"
            test_id: "IT-AUTH-001"
            test_path: "tests/integration/auth-flow.test.ts"
        implemented_in:
          - file: "src/auth/credential-validator.ts"
            component: "CredentialValidator"
            lines: "45-89"
```

**Track Requirements**:
- **Quick**: Optional, forward trace recommended
- **Standard**: Backward trace required for 80%+ requirements, forward trace required
- **Enterprise**: Full bi-directional traceability required (100% coverage)

---

## 7. Quality Validation

### 7.1 Eight-Dimension Scoring Matrix

| Category | Weight | Subcriteria |
|----------|--------|-------------|
| **Completeness** | 20% | All sections present, subsections covered, no gaps |
| **Technical Accuracy** | 18% | Correct patterns, valid schemas, feasible approach |
| **Clarity & Readability** | 10% | Clear prose, organization, effective diagrams |
| **Testability** | 15% | EARS notation, acceptance criteria, measurable |
| **Implementability** | 14% | Sufficient detail, no ambiguity |
| **Resilience Design** | 10% | Error handling, edge cases, degradation |
| **Security** | 5% | Threats addressed, access control, data protection |
| **Operability** | 8% | Monitoring, logging, deployment, observability |

> **Note**: Operability increased from 5% to 8% (v2.3.0) to better reflect production readiness requirements.
> For brownfield changes touching critical paths, Operability weight increases to **10%**.

**Brownfield Operability Adjustment**:
```yaml
operability_weight_adjustment:
  default_weight: 8
  brownfield_critical_path_weight: 10
  applies_when:
    - "Change touches high-traffic endpoints"
    - "Modification affects monitoring/alerting systems"
    - "Update to data pipeline or batch processing"
    - "Changes to deployment or infrastructure code"
  rationale: |
    Brownfield changes to critical paths require stronger operability
    guarantees since failures impact existing production traffic.
```

### 6.1.1 Risk-Adjusted Quality Thresholds

> **BF-06**: Quality thresholds determined by highest-risk characteristic of the change

**Principle**: Quality thresholds use predefined tiers based on risk level, not additive calculations. This ensures thresholds are always meaningful (0-100% scale) and easier to reason about.

**Tier Definitions**:

```yaml
risk_adjusted_quality_thresholds:
  overview: |
    Quality thresholds are determined by the highest-risk characteristic
    of the change. Thresholds are predefined, not calculated additively.
    Scale: 0-100%, where 100% represents exemplary quality for that risk level.

  threshold_tiers:
    tier_critical:
      threshold: 95
      label: "Critical Risk"
      applies_when:
        - "Modifies authentication or authorization flow"
        - "Touches payment processing code"
        - "Changes security-sensitive operations (encryption, secrets)"
        - "Modifies base classes used by 5+ consumers"
        - "Changes data persistence layer affecting >100K records"

    tier_high:
      threshold: 90
      label: "High Risk"
      applies_when:
        - "Modifies shared abstractions (interfaces, base classes)"
        - "Changes data persistence layer"
        - "Affects user-facing APIs with external consumers"
        - "Modifies shared utilities used by 3+ modules"

    tier_elevated:
      threshold: 85
      label: "Elevated Risk"
      applies_when:
        - "Modifies code with deep dependency chains (5+ levels)"
        - "Changes affecting 15+ files"
        - "Touches high-traffic endpoints (>1000 req/min)"

    tier_standard:
      threshold: 80
      label: "Standard Risk"
      applies_when:
        - "Default for all other changes"
        - "Isolated new feature modules"
        - "Internal tooling modifications"

  threshold_selection:
    rule: "Apply the HIGHEST applicable tier"
    rationale: |
      If a change touches both a shared utility (High: 90%) and
      an auth flow (Critical: 95%), the threshold is 95%.
```

**Examples**:

| Scenario | Applicable Tiers | Final Threshold |
|----------|------------------|-----------------|
| Modify base class used by auth flow | Critical (auth) + High (base class) | **95%** (Critical) |
| Add utility to shared module | High (shared utility) | **90%** (High) |
| Refactor touching 20 files | Elevated (15+ files) | **85%** (Elevated) |
| Isolated new feature module | Standard (default) | **80%** (Standard) |

**User Interface**:
```
Quality Threshold: 95% (Critical Risk)
├─ Tier: Critical
├─ Reason: Modifies authentication flow
├─ Other applicable tiers: High (shared base class)
└─ Note: Highest applicable tier selected
```

**Override Options**:
```yaml
user_override:
  flag: "--quality-threshold {{value}}"
  validation: "value >= 70% AND value <= 100%"
  justification_required: "when override_value < calculated_threshold"
  audit: "Override recorded in spec metadata"
  warning: |
    Overriding below calculated threshold requires justification.
    Common valid reasons: prototype/spike, internal tooling, time-boxed experiment
```

### 6.2 Scoring Rubric

```yaml
scoring_rubric:
  1-2: "Critical gaps, missing major elements, unusable"
  3-4: "Significant gaps, partial coverage, needs major revision"
  5-6: "Adequate, covers basics, some gaps or ambiguity"
  7-8: "Good, comprehensive coverage, minor gaps"
  9-10: "Excellent, exceeds requirements, exemplary"
```

### 6.3 Quality Attributes (IEEE/ISO)

1. **Unambiguous** - Single interpretation possible
2. **Complete** - All requirements documented
3. **Consistent** - No internal conflicts
4. **Verifiable** - Can be objectively tested
5. **Traceable** - Linked to source and implementation
6. **Modifiable** - Easy to update without ripple effects

### 6.4 Quality Gates

| Gate | Trigger | Minimum Score | Actions on Fail |
|------|---------|---------------|-----------------|
| **Draft Gate** | Before review | 60% | Flag gaps, suggest additions |
| **Review Gate** | Before approval | 70% | Block until resolved |
| **Approval Gate** | Before implementation | 80% | Require explicit override |
| **Release Gate** | Enterprise only | 90% | Mandatory compliance sign-off |

### 6.4.1 Pattern Conformance Gate

> **BF-07**: Mandate implementation alignment with existing project patterns

**Purpose**: Brownfield code must conform to existing patterns to maintain consistency.

**Gate Definition**:
```yaml
gate_5_pattern_conformance:
  id: "gate_5_pattern_conformance"
  type: "quality_gate"
  mandatory_for: [standard, enterprise]
  optional_for: [quick]
  trigger: "Before template rendering"
  weight_in_scoring:
    dimension: "Implementability"
    contribution: "30% of implementability score"
```

**Pattern Sources**:

| Source | Purpose | Query Approach |
|--------|---------|----------------|
| **Context7** | Framework/library patterns | "{{framework}} best practices for {{feature_type}}" |
| **Serena** | Project conventions | `read_memory('project_conventions')` + `find_symbol()` |
| **Auggie** | Similar implementations | "Implementations similar to {{feature_type}}" |

**Validation Process**:

```yaml
pattern_validation:
  step_1_discover:
    - Query Context7 for framework patterns
    - Query Serena for project conventions
    - Query Auggie for similar implementations

  step_2_extract:
    - Component structure patterns
    - Naming conventions
    - API design patterns
    - Error handling patterns

  step_3_validate:
    naming_conformance:
      check: "Proposed names follow project naming conventions"
      severity: warning

    structure_conformance:
      check: "Component structure matches framework patterns"
      severity: warning

    api_conformance:
      check: "API design follows established patterns"
      severity: error  # For public APIs

  step_4_report:
    conformance_score: "(conforming_items / total_items) * 100"
    threshold: "80% minimum"
```

**Conformance Report Template**:
```markdown
## Pattern Conformance Report

**Score**: {{score}}% ({{status}})

### Patterns Applied
{{#each applied_patterns}}
- ✅ {{pattern_name}}: {{description}}
  - Source: {{source}}
{{/each}}

### Deviations
{{#each deviations}}
- {{severity_icon}} {{deviation_description}}
  - Expected: {{expected_pattern}}
  - Proposed: {{proposed_approach}}
  - Justification Required: {{justification_required}}
{{/each}}

### Recommendations
{{#each recommendations}}
- {{recommendation}}
{{/each}}
```

**Deviation Handling**:
```yaml
deviation_types:
  justified:
    description: "Deviation with valid technical reason"
    requirements: [justification, approval_recorded]
    example: "Using class component for error boundary (React limitation)"

  unjustified:
    description: "Deviation without technical reason"
    action: "Block until justified or corrected"
    override: "--allow-pattern-deviation (with audit log)"

  pattern_evolution:
    description: "Proposing new pattern for the project"
    requirements: [document_in_adr, optional_migration_plan]
    example: "Introducing new error handling pattern project-wide"
```

### 6.5 Validation Pipeline

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ 1. SYNTAX       │ --> │ 2. SCHEMA       │ --> │ 3. STRUCTURAL   │
│ Parse template  │     │ Validate JSON   │     │ Apply rules     │
│ Check nesting   │     │ schema matches  │     │ Check patterns  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        v                       v                       v
   ┌────────────────────────────────────────────────────────┐
   │                  VALIDATION REPORT                      │
   │  ✓ Syntax: PASS                                        │
   │  ✓ Schema: PASS (metadata: valid, requirements: valid) │
   │  ⚠ Structural: 1 warning (missing accessibility)       │
   │  Overall: PASS WITH WARNINGS (Score: 78%)              │
   └────────────────────────────────────────────────────────┘
```

---

## 8. Adversarial Validation Engine

> **v2.4.0**: SpecDebateEngine - Conditional adversarial debates at critical decision points

### 8.1 Overview

The Adversarial Validation Engine (SpecDebateEngine) provides structured multi-expert debates at strategic points in the spec generation flow. Based on adversarial synthesis from 5 expert personas (Architect, Requirements, QA, Operations, Performance), the engine focuses debates where they deliver maximum value while respecting performance constraints.

**Design Principles**:
- **Conditional Activation**: Debates trigger only when genuinely needed (not always-on)
- **Unified Mechanism**: Single engine vs. scattered debate points
- **Traceable Outputs**: All findings linked to specific spec sections
- **Testable Results**: Mandatory test stub generation
- **Performance-Bounded**: Hard token/time limits to prevent process bloat

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SPECDEBATE ENGINE ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ENTRY POINTS                    UNIFIED ENGINE                OUTPUT       │
│  ────────────                    ──────────────                ──────       │
│                                                                             │
│  ┌───────────────┐              ┌─────────────────────┐                    │
│  │ Phase 2       │──────────────│                     │                    │
│  │ Assumption    │  Triggers    │   SpecDebateEngine  │    ┌────────────┐  │
│  │ Validation    │──────────────│                     │───▶│ Traced     │  │
│  └───────────────┘              │  ┌───────────────┐  │    │ Findings   │  │
│                                 │  │ Expert Panel  │  │    └────────────┘  │
│  ┌───────────────┐              │  │ ───────────── │  │                    │
│  │ BF-07         │──────────────│  │ Core: Wiegers │  │    ┌────────────┐  │
│  │ Pattern       │  Triggers    │  │       Adzic   │  │───▶│ Test       │  │
│  │ Conformance   │──────────────│  │       Fowler  │  │    │ Stubs      │  │
│  └───────────────┘              │  │               │  │    └────────────┘  │
│                                 │  │ Contextual:   │  │                    │
│                                 │  │   Nygard      │  │    ┌────────────┐  │
│                                 │  │   Newman      │  │───▶│ Confidence │  │
│                                 │  │   Crispin     │  │    │ Delta      │  │
│                                 │  │   Gregory     │  │    └────────────┘  │
│                                 │  │   Hohpe       │  │                    │
│                                 │  └───────────────┘  │                    │
│                                 │                     │                    │
│                                 │  ┌───────────────┐  │                    │
│                                 │  │ Debate Modes  │  │                    │
│                                 │  │ ───────────── │  │                    │
│                                 │  │ lite: 2 exp   │  │                    │
│                                 │  │ standard: 4   │  │                    │
│                                 │  │ deep: 6 exp   │  │                    │
│                                 │  └───────────────┘  │                    │
│                                 └─────────────────────┘                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Entry Point 1: Assumption Validation Debates

> **Location**: Phase 2 Validation (Section 4.3)
> **Rationale**: Earliest actionable intervention point - fixes are cheap here

**Conditional Activation**:

```yaml
assumption_debate_triggers:
  activate_when:
    assumption_count: "> 5"              # More than 5 unstated assumptions detected
    confidence_score: "< 0.7"            # Low confidence in gathered requirements
    high_risk_flag: true                 # Critical domain (auth, payment, security)
    contradiction_detected: true         # Conflicting requirements identified

  skip_when:
    quick_track: true                    # Quick track skips validation phase
    assumption_count: "<= 3"             # Few assumptions, debate overhead not justified
    confidence_score: "> 0.85"           # High confidence, no debate needed
    user_flag: "--skip-debate"           # Explicit user override
```

**Debate Process**:

```yaml
assumption_debate:
  trigger_point: "After assumption collection in Phase 2"

  expert_panel:
    core:
      - wiegers:   "Challenge requirement completeness"
      - adzic:     "Demand concrete examples for assumptions"
    contextual:
      - fowler:    "Architectural assumption validity"
      - crispin:   "Testing perspective on assumptions"

  debate_structure:
    round_1_challenge:
      - "What evidence supports assumption {{n}}?"
      - "What happens if assumption {{n}} is wrong?"
      - "Who validated this assumption?"

    round_2_alternatives:
      - "What alternative interpretations exist?"
      - "What edge cases would break this assumption?"

    round_3_resolution:
      - "Can we convert assumption to explicit requirement?"
      - "What test would validate this assumption?"

  max_rounds: 2
  debate_depth: "lite | standard"  # Based on track
```

**Output Schema**:

```yaml
assumption_debate_output:
  traced_findings:
    format: "FINDING-{n}: Section {ref} → {issue} → {recommendation}"
    example: |
      FINDING-1: Section 3.2 (User Authentication) →
        Assumed OAuth always available →
        Add explicit fallback requirement for OAuth unavailability

  testability_stubs:
    format: "TEST-{n}: Given {context} When {action} Then {outcome}"
    example: |
      TEST-1: Given OAuth service is unavailable
              When user attempts login
              Then system offers alternative authentication method

  confidence_delta:
    before: 0.65
    after: 0.82
    improvement_source: "3 assumptions converted to requirements, 2 invalidated"

  dissent_record:  # Optional - preserve minority viewpoints
    - expert: "adzic"
      position: "Assumption 4 needs user research, not debate"
      resolution: "Deferred to user story mapping phase"
```

### 8.3 Entry Point 2: Pattern Conformance Debates

> **Location**: BF-07 Pattern Conformance Gate (Section 6.4.1)
> **Rationale**: Catches systemic pattern drift before implementation

**Conditional Activation**:

```yaml
pattern_debate_triggers:
  activate_when:
    deviation_score: "> 0.3"             # Significant deviation from established patterns
    brownfield_context: true             # Only for brownfield projects
    pattern_exception_requested: true    # Explicit request to deviate
    critical_path_affected: true         # Changes touch critical system paths

  skip_when:
    greenfield_project: true             # No existing patterns to conform to
    deviation_score: "<= 0.15"           # Minor deviation, not worth debating
    approved_exception: true             # Pre-approved pattern deviation
    user_flag: "--skip-pattern-debate"   # Explicit user override
```

**Debate Process**:

```yaml
pattern_conformance_debate:
  trigger_point: "After pattern analysis in BF-07 gate"

  expert_panel:
    core:
      - fowler:    "Architectural pattern analysis"
      - nygard:    "Operational resilience patterns"
    contextual:
      - newman:    "Service boundary patterns"
      - hohpe:     "Integration patterns"

  debate_structure:
    round_1_deviation_analysis:
      - "Why does this deviate from {{pattern_name}}?"
      - "What problem does the deviation solve?"
      - "What precedent does this set?"

    round_2_impact_assessment:
      - "How will existing consumers handle this change?"
      - "What migration path exists?"
      - "What monitoring will detect issues?"

    round_3_resolution:
      - "Is deviation justified and documented?"
      - "What guardrails prevent pattern drift?"
      - "What tests verify pattern compliance?"

  max_rounds: 2
  debate_depth: "standard | deep"  # Based on deviation severity
```

**Output Schema**:

```yaml
pattern_debate_output:
  traced_findings:
    format: "PATTERN-{n}: {pattern} deviation in {location} → {justification} → {mitigation}"
    example: |
      PATTERN-1: Repository pattern deviation in UserService →
        Justified: Direct DB access needed for batch operations →
        Mitigation: Isolate to BatchProcessor class with explicit bypass annotation

  testability_stubs:
    format: "PATTERN-TEST-{n}: Verify {pattern} compliance for {component}"
    example: |
      PATTERN-TEST-1: Verify Repository pattern compliance
        Given UserService.batchUpdate() is called
        When operation completes
        Then only BatchProcessor bypasses Repository pattern
        And audit log records pattern bypass with justification

  deviation_registry:
    pattern_name: "Repository Pattern"
    deviation_type: "justified"
    approval_status: "debate_approved"
    justification: "Batch operations require direct DB access for performance"
    guardrails:
      - "Isolated to BatchProcessor class"
      - "Explicit @PatternBypass annotation required"
      - "Audit logging for all bypasses"
```

### 8.4 Performance Guardrails

> **Rationale**: Prevent "process theater" - debates must deliver value, not just activity

**Token Limits**:

```yaml
debate_token_limits:
  lite:
    max_tokens: 5000
    max_rounds: 1
    experts: 2
    timeout_seconds: 60

  standard:
    max_tokens: 15000
    max_rounds: 2
    experts: 4
    timeout_seconds: 120

  deep:
    max_tokens: 40000
    max_rounds: 3
    experts: 6
    timeout_seconds: 300
```

**Depth Selection**:

```yaml
debate_depth_selection:
  lite:
    triggers:
      - quick_track: true
      - low_risk: true
      - single_assumption: true
    purpose: "Rapid sanity check for minor issues"

  standard:
    triggers:
      - standard_track: true
      - moderate_risk: true
      - multiple_assumptions: true
    purpose: "Balanced analysis for typical specifications"

  deep:
    triggers:
      - enterprise_track: true
      - high_risk: true
      - critical_deviation: true
      - security_domain: true
    purpose: "Comprehensive analysis for critical decisions"
```

**User Control Flags**:

```yaml
debate_control_flags:
  --debate-depth:
    options: [skip, lite, standard, deep]
    default: "auto"  # Determined by triggers
    description: "Override automatic debate depth selection"

  --debate-focus:
    options: [assumptions, patterns, both, none]
    default: "auto"  # Determined by context
    description: "Limit debates to specific entry points"

  --debate-verbose:
    options: [true, false]
    default: false
    description: "Include full debate transcript in output"

  --debate-experts:
    options: "comma-separated expert names"
    default: "auto"  # Based on context
    description: "Override expert panel selection"
```

### 8.5 Expert Panel Configuration

**Core Experts** (Always Available):

| Expert | Domain | Primary Focus | Signature Question |
|--------|--------|---------------|-------------------|
| **Wiegers** | Requirements | Completeness, clarity | "Is this requirement testable?" |
| **Adzic** | Examples | Concrete scenarios | "Can you give a specific example?" |
| **Fowler** | Architecture | Patterns, structure | "Does this fit the existing architecture?" |

**Contextual Experts** (Activated by Domain):

| Expert | Domain | Activation Context | Signature Question |
|--------|--------|-------------------|-------------------|
| **Nygard** | Operations | Brownfield, resilience | "What happens when this fails?" |
| **Newman** | Services | Microservices, boundaries | "Is this the right service boundary?" |
| **Crispin** | Testing | Quality, coverage | "How will we test this?" |
| **Gregory** | Testing | Acceptance criteria | "What does 'done' look like?" |
| **Hohpe** | Integration | APIs, messaging | "How does this integrate?" |

**Expert Activation Rules**:

```yaml
expert_activation:
  brownfield_context:
    add: [nygard, newman]
    reason: "Operational resilience and service boundaries matter"

  testing_focus:
    add: [crispin, gregory]
    reason: "Testing perspective strengthens requirements"

  integration_context:
    add: [hohpe]
    reason: "Integration patterns need specialized review"

  security_domain:
    add: [nygard]
    reason: "Security requires failure mode analysis"
```

### 8.6 Debate Modes

**DISCUSSION Mode** (Default):

```yaml
discussion_mode:
  purpose: "Collaborative multi-perspective analysis"
  interaction: "Experts build on each other's insights"
  output: "Converged findings with consensus recommendations"
  use_when: "Standard assumptions, moderate deviations"
```

**CRITIQUE Mode** (Adversarial):

```yaml
critique_mode:
  purpose: "Stress-test through structured disagreement"
  interaction: "Experts challenge positions with evidence"
  output: "Productive tensions resolved, minority views preserved"
  use_when: "High-risk decisions, justified deviations"
```

**SOCRATIC Mode** (Educational):

```yaml
socratic_mode:
  purpose: "Develop strategic thinking through questioning"
  interaction: "Experts ask probing questions, user reflects"
  output: "Learning insights, deeper understanding"
  use_when: "Complex assumptions, pattern rationale needed"
```

### 8.7 Integration with Spec Generation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SPEC GENERATION FLOW WITH DEBATES                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INPUT → COMPLEXITY ROUTER → QUESTION FRAMEWORK                             │
│                                      │                                      │
│                                      ▼                                      │
│                            ┌─────────────────┐                              │
│                            │  Phase 1:       │                              │
│                            │  DISCOVERY      │                              │
│                            └────────┬────────┘                              │
│                                     │                                       │
│                                     ▼                                       │
│                            ┌─────────────────┐                              │
│                            │  Phase 2:       │                              │
│                            │  VALIDATION     │──┐                           │
│                            └────────┬────────┘  │                           │
│                                     │           │                           │
│                                     │    ┌──────▼──────┐                    │
│                                     │    │ ASSUMPTION  │                    │
│                                     │    │ DEBATE?     │ ← Conditional      │
│                                     │    └──────┬──────┘                    │
│                                     │           │                           │
│                                     ◀───────────┘                           │
│                                     │                                       │
│                                     ▼                                       │
│                            ┌─────────────────┐                              │
│                            │  Phase 3:       │                              │
│                            │  COMPLETION     │                              │
│                            └────────┬────────┘                              │
│                                     │                                       │
│                                     ▼                                       │
│                            ┌─────────────────┐                              │
│                            │  TEMPLATE       │                              │
│                            │  ENGINE         │                              │
│                            └────────┬────────┘                              │
│                                     │                                       │
│                                     ▼                                       │
│                            ┌─────────────────┐                              │
│                            │  BF-07 PATTERN  │──┐                           │
│                            │  CONFORMANCE    │  │                           │
│                            └────────┬────────┘  │                           │
│                                     │           │                           │
│                                     │    ┌──────▼──────┐                    │
│                                     │    │ PATTERN     │                    │
│                                     │    │ DEBATE?     │ ← Conditional      │
│                                     │    └──────┬──────┘                    │
│                                     │           │                           │
│                                     ◀───────────┘                           │
│                                     │                                       │
│                                     ▼                                       │
│                            ┌─────────────────┐                              │
│                            │  QUALITY        │                              │
│                            │  VALIDATION     │                              │
│                            └────────┬────────┘                              │
│                                     │                                       │
│                                     ▼                                       │
│                                  OUTPUT                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. AI Optimization

### 9.1 EARS Notation

**Easy Approach to Requirements Syntax** - testable requirement format:

| Type | Template | Example |
|------|----------|---------|
| **Ubiquitous** | The system shall [action] | The system shall encrypt all passwords |
| **Event-Driven** | When [event], the system shall [action] | When user logs in, the system shall create session |
| **State-Driven** | While [state], the system shall [action] | While session active, the system shall track activity |
| **Optional** | Where [feature], the system shall [action] | Where 2FA enabled, the system shall verify OTP |
| **Complex** | If [condition], then the system shall [action] | If 3 failed attempts, then the system shall lock account |

**Full Format**:
```markdown
## REQ-AUTH-001: Session Timeout

WHEN a user session exceeds 30 minutes of inactivity
THE SYSTEM SHALL automatically log out the user
AND redirect to the login page
SO THAT unauthorized access is prevented

### Acceptance Criteria
- [ ] Timer resets on any user activity
- [ ] Warning displayed at 25 minutes
- [ ] Graceful handling of unsaved work
```

### 7.2 RFC 2119 Keywords

| Keyword | Meaning | AI Interpretation |
|---------|---------|-------------------|
| **MUST** | Absolute requirement | Always implement |
| **MUST NOT** | Absolute prohibition | Never implement |
| **SHOULD** | Strong recommendation | Implement unless justified |
| **SHOULD NOT** | Strong discouragement | Avoid unless justified |
| **MAY** | Optional | Implement if beneficial |

### 7.3 AI Context Block

```yaml
ai_context:
  # Classification
  domain: feature | infrastructure | documentation | api
  complexity:
    level: simple | moderate | complex
    rationale: "Brief explanation"
  track: quick | standard | enterprise

  # Technology Stack
  technology:
    primary: ["TypeScript", "React"]
    frameworks: ["Next.js", "TailwindCSS"]
    databases: ["PostgreSQL"]
    dependencies:
      required:
        - package: "@auth/core"
          version: "^2.0"

  # Agent Profile
  agent_profile:
    role: implementation
    capabilities:
      - scope: "src/**/*.ts"
        actions: [read, edit, create]
    limitations:
      - "MUST NOT modify configuration files"
      - "MUST NOT access external APIs without approval"

  # Quality Gates
  quality_gates:
    test_coverage:
      minimum: 80
      required: true
    type_safety: required
    lint_clean: required

  # Confidence Thresholds
  confidence_thresholds:
    proceed_automatically: 0.90
    request_confirmation: 0.70
    escalate_to_human: 0.50

  # Parsing Hints
  parsing_hints:
    - "Requirements IDs follow pattern: REQ-[FEATURE]-[NUMBER]"
    - "Priority uses MoSCoW: MUST, SHOULD, MAY, WONT"
    - "Sections are delineated by H2 headers (##)"
```

### 7.3.1 Track-Specific Context Schemas

**Principle**: Context complexity should match track complexity.

| Track | Required Fields | Max Lines | Example |
|-------|-----------------|-----------|---------|
| Quick | domain, complexity | 5 | `{domain: feature, complexity: simple}` |
| Standard | domain, complexity, technology, quality_gates | 20 | See below |
| Enterprise | All fields | 50 | Full schema (above) |

**Quick Track Schema**:
```yaml
ai_context:
  domain: feature       # Required: feature | api | infrastructure
  complexity: simple    # Required: simple | moderate
  technology: ["TypeScript"]  # Optional: single primary tech
```

**Standard Track Schema**:
```yaml
ai_context:
  domain: feature
  complexity:
    level: moderate
    rationale: "Multi-component feature with API integration"
  technology:
    primary: ["TypeScript", "React"]
    frameworks: ["Next.js"]
  quality_gates:
    test_coverage: 80
    lint_clean: true
```

**Enterprise Track Schema**: Uses full schema from Section 6.3 (above).

**Schema Validation**:
```yaml
schema_validation:
  engine: zod
  strict_mode: true
  track_schemas:
    quick: QuickContextSchema      # 2 required, 1 optional field
    standard: StandardContextSchema # 4 required fields
    enterprise: EnterpriseContextSchema # All fields required
```

### 7.4 Structured Output Schemas

**Requirement Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "type", "statement"],
  "properties": {
    "id": {"type": "string", "pattern": "^REQ-[A-Z]+-\\d{3}$"},
    "type": {"enum": ["ubiquitous", "event-driven", "state-driven", "optional", "complex"]},
    "priority": {"enum": ["MUST", "SHOULD", "MAY", "WONT"]},
    "statement": {
      "type": "object",
      "properties": {
        "when": {"type": "string"},
        "the_system_shall": {"type": "string"},
        "so_that": {"type": "string"}
      }
    },
    "acceptance_criteria": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1
    }
  }
}
```

### 7.5 Dual-Format Output

Generate both formats for maximum utility:

1. **Human-Readable**: Full markdown with prose, context, rationale
2. **AI-Optimized**: Structured YAML/JSON for agent consumption

---

## 10. Workflow Process

### 10.1 Six-Phase Workflow (Extended for Brownfield)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        SPEC GENERATION WORKFLOW                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PHASE 1         PHASE 2         PHASE 3         PHASE 4                │
│  ┌───────┐       ┌───────┐       ┌───────┐       ┌───────┐              │
│  │INPUT  │──────▶│ROUTE  │──────▶│ELICIT │──────▶│RENDER │              │
│  │       │       │       │       │       │       │       │              │
│  │Prompt │       │Track  │       │Q&A    │       │Spec   │              │
│  │Context│       │Select │       │Flow   │       │Output │              │
│  └───────┘       └───────┘       └───────┘       └───────┘              │
│      │               │               │               │                   │
│      │               │               │               │                   │
│      ▼               ▼               ▼               ▼                   │
│  ┌───────┐       ┌───────┐       ┌───────┐       ┌───────┐              │
│  │Analyze│       │Quick  │       │Phase 1│       │Template│              │
│  │Domain │       │Std    │       │Phase 2│       │Render │              │
│  │Scope  │       │Ent    │       │Phase 3│       │        │              │
│  └───────┘       └───────┘       └───────┘       └───────┘              │
│                                                       │                  │
│                                                       ▼                  │
│  PHASE 5                                         PHASE 6                │
│  ┌───────┐                                       ┌───────┐              │
│  │VALIDATE│◀──────────────────────────────────────│SCORE  │              │
│  │       │                                       │       │              │
│  │Quality│        ┌─────────────────────┐        │8-dim  │              │
│  │Gates  │        │   < 80%? ITERATE    │        │Matrix │              │
│  └───────┘        └─────────────────────┘        └───────┘              │
│      │                      │                                           │
│      │                      ▼                                           │
│      │               ┌───────────┐                                      │
│      └──────────────▶│  OUTPUT   │                                      │
│           ≥80%       │           │                                      │
│                      │Spec + JSON│                                      │
│                      │+ AI Block │                                      │
│                      └───────────┘                                      │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Phase Details (Updated)

| Phase | Purpose | Key Activities | Outputs |
|-------|---------|----------------|---------|
| **0a. Onboarding** *(brownfield, fresh agent)* | Bootstrap agent knowledge | Serena memory check, architecture discovery, convention extraction, critical path ID | Agent memories |
| **0b. Context** *(brownfield)* | Acquire codebase context | Auggie query, impact analysis, baseline capture | Impact analysis |
| **0c. Prior Art** *(all projects)* | Research existing solutions | GitHub search, scoring, shallow scan, deep dive, debate | Prior art analysis |
| **1. Input** | Capture initial context | Parse prompt, detect domain, analyze scope | Context analysis |
| **2. Route** | Select appropriate track | Score complexity (+ impact + prior art insights), recommend track | Track selection |
| **3. Elicit** | Gather requirements | Execute question framework + BF questions | Answered questions |
| **4. Render** | Generate specification | Apply template + BC sections + prior art section, interpolate variables | Draft spec |
| **5. Validate** | Ensure quality | Apply 8-dim scoring + pattern conformance | Validation report |
| **6. Output** | Produce final deliverables | Generate markdown + JSON + AI block + history artifacts | Complete spec |

### 10.3 Decision Points

| Decision | Criteria | Outcomes |
|----------|----------|----------|
| **Track Override** | User request | Accept recommendation or manual selection |
| **Question Skip** | High confidence (>95%) | Proceed with default or ask |
| **Iteration Loop** | Score < 80% | Re-elicit gaps or accept with warning |
| **Approval Gate** | Enterprise track | Require stakeholder sign-off |

### 10.4 Iteration Control and Escape Options

**Iteration Limits**:
```yaml
iteration_control:
  max_iterations: 3
  improvement_threshold: 5%  # Must improve by 5% per iteration
  time_limits:
    quick: 5_minutes
    standard: 15_minutes
    enterprise: 30_minutes
```

**User Escape Options**:

| Option | Min Score | Requires | Output |
|--------|-----------|----------|--------|
| **Accept with Warning** | 60% | Acknowledgment | Spec with "DRAFT" banner |
| **Force Accept** | 50% | Justification | Spec with justification in metadata |
| **Pause and Resume** | Any | None | Checkpoint saved |
| **Export for Manual** | Any | None | Partial spec + gap list |

**Accept with Warning**:
```yaml
accept_with_warning:
  threshold: 60%
  prompt: |
    Spec scored {{SCORE}}% (below 80% threshold).

    Missing elements:
    {{#EACH gaps}}
    - {{category}}: {{description}}
    {{/EACH}}

    Accept anyway? [y/N]
  output:
    banner: "⚠️ DRAFT - Score: {{SCORE}}% - Review Required"
    metadata:
      accepted_below_threshold: true
      gaps: [{{GAP_LIST}}]
```

**Pause and Resume**:
```yaml
checkpoint:
  location: ".spec-generator/checkpoints/{{SPEC_ID}}/"
  contents:
    - current_phase: string
    - elicited_answers: object
    - partial_spec: string
    - validation_report: object
  resume_command: "/sc:spec --resume {{SPEC_ID}}"
  expiration: "7 days"
```

**Export for Manual Completion**:
```yaml
export_for_manual:
  output_files:
    - "{{SPEC_NAME}}.partial.md"   # Current spec content
    - "{{SPEC_NAME}}.gaps.md"      # List of gaps to address
    - "{{SPEC_NAME}}.context.yaml" # Context for manual continuation
```

---

## 11. Tool Integration

### 11.1 MCP Server Integration

| Server | Role | Usage | Activation |
|--------|------|-------|------------|
| **Sequential** | Complex reasoning | Question flow, validation, analysis | Always |
| **Context7** | Documentation | Templates, EARS examples, best practices, patterns | Always |
| **Serena** | Project memory | Session persistence, checkpoints, context, conventions | Always |
| **Playwright** | Validation testing | Schema validation, file checks, EARS parsing | `--validate` or Enterprise |
| **Auggie** | Codebase intelligence | Semantic search, component discovery, impact analysis | Brownfield mode |

### 11.1.1 Auggie MCP Integration

> **BF-01**: Semantic codebase understanding for brownfield projects

**Purpose**: Enable context acquisition before spec generation using embedding-based retrieval.

```yaml
auggie_workflow:
  activation:
    automatic:
      - brownfield_mode: true
      - existing_codebase: ">10 files"
    manual:
      - flag: "--auggie"
      - flag: "--brownfield"

  operations:
    domain_discovery:
      tool: "mcp__auggie-mcp__codebase-retrieval"
      query: "Components related to {{feature_domain}}"
      output: affected_components

    pattern_extraction:
      tool: "mcp__auggie-mcp__codebase-retrieval"
      query: "Existing patterns in {{feature_domain}}"
      output: existing_patterns

    dependency_mapping:
      tool: "mcp__auggie-mcp__codebase-retrieval"
      query: "Dependencies of {{affected_components}}"
      output: dependency_graph

  post_implementation:
    trigger: "spec_marked_implemented"
    action: "Queue modified files for re-indexing"

  error_handling:
    auggie_unavailable:
      fallback: "Grep + Glob file-based discovery"
      warning: "⚠️ Semantic analysis unavailable"
      quality_impact: "-10% confidence"
```

### 11.1.2 Playwright Validation Tests

**Purpose**: Automated validation of generated specifications.

**Schema Validation**:
```yaml
playwright_validation:
  schema_tests:
    - name: "AI context valid YAML"
      action: parse_yaml(spec.context.yaml)
      expect: no_errors

    - name: "Requirement IDs follow pattern"
      action: regex_match(spec.md, /REQ-[A-Z]+-\d{3}/)
      expect: all_requirements_match

    - name: "EARS statements well-formed"
      action: verify_ears_syntax(spec.md)
      expect:
        has_when_clause: true
        has_shall_clause: true
        has_so_that_clause: optional
```

**File Integrity Tests**:
```yaml
  file_tests:
    - name: "Referenced files exist"
      action: check_file_refs(spec.md)
      expect: all_exist

    - name: "Output directory writable"
      action: check_permissions(output_path)
      expect: writable
```

**Integration Readiness Tests**:
```yaml
  integration_tests:
    - name: "Spec loadable by task generator"
      action: load_spec_in_downstream_tool(spec.md)
      expect: parses_successfully
```

**Activation Conditions**:
```yaml
playwright_activation:
  mandatory:
    - track: enterprise
    - flag: --validate
    - flag: --comprehensive
  optional:
    - validation_score: < 80%  # Re-validate after iteration
```

### 11.2 File Operations

```yaml
file_patterns:
  spec_output:
    pattern: "specs/{feature-name}.spec.md"
    track_variants:
      quick: "specs/quick/{feature-name}.spec.md"
      standard: "specs/{feature-name}.spec.md"
      enterprise: "specs/enterprise/{feature-name}.spec.md"

  ai_context:
    pattern: "specs/{feature-name}.context.yaml"

  templates:
    location: ".spec-generator/templates/"

  customization:
    location: ".spec-generator/customize.yaml"
```

### 11.3 Integration Verification

**Critical Learning** (from failure analysis):

> A spec→roadmap→tasklist pipeline optimized for deliverables will miss integration failures. The pipeline MUST include explicit verification gates between components and mandatory end-to-end validation.

**Required Verification Steps**:

1. **Feasibility Analysis**: Before committing to approach, verify interfaces exist
2. **Integration Milestones**: Explicit data flow verification between phases
3. **Behavior-Based Done**: Task completion = behavior verified, not code exists
4. **User Path Testing**: Test actual user workflow, not just unit functions
5. **Manual Validation**: Run actual command, verify actual output

---

## 12. Development History Artifacts

> **BF-05**: Ensure spec generation produces artifacts that update project development history

### 11.1 Overview

Brownfield development requires maintaining project history for:
- Architectural decision tracking (why changes were made)
- Changelog continuity (what changed and when)
- Agent memory persistence (context for future AI interactions)
- Team knowledge transfer (onboarding and documentation)

### 10.2 Architectural Decision Record (ADR)

**Generation**: Standard and Enterprise tracks

```yaml
adr_artifact:
  location: "docs/adr/ADR-{{NUMBER}}-{{SLUG}}.md"
  auto_number: true
  number_source: "count(docs/adr/*.md) + 1"

  template: |
    # ADR-{{NUMBER}}: {{TITLE}}

    **Date**: {{DATE}}
    **Status**: Proposed | Accepted | Deprecated | Superseded
    **Spec**: {{SPEC_FILE}}

    ## Context
    {{PROBLEM_STATEMENT}}

    ## Decision
    {{SOLUTION_SUMMARY}}

    ## Consequences

    ### Positive
    {{#each positive_consequences}}
    - {{this}}
    {{/each}}

    ### Negative
    {{#each negative_consequences}}
    - {{this}}
    {{/each}}

    ## Alternatives Considered
    {{#each alternatives}}
    ### {{name}}
    - **Pros**: {{pros}}
    - **Cons**: {{cons}}
    - **Why Rejected**: {{rejection_reason}}
    {{/each}}

  population:
    TITLE: "metadata.title"
    PROBLEM_STATEMENT: "problem_statement"
    SOLUTION_SUMMARY: "solution_design.overview"
    alternatives: "alternatives_considered"
```

### 10.3 Changelog Entry

**Generation**: All tracks

```yaml
changelog_artifact:
  location: "CHANGELOG.md"
  mode: "append to [Unreleased] section"
  format: "Keep a Changelog"

  template: |
    ### {{CATEGORY}}

    - {{SUMMARY}} ([{{SPEC_ID}}]({{SPEC_PATH}}))
      {{#if breaking_change}}
      - **BREAKING**: {{breaking_description}}
      {{/if}}

  categories:
    Added: "New features"
    Changed: "Changes to existing functionality"
    Deprecated: "Features marked for removal"
    Removed: "Removed features"
    Fixed: "Bug fixes"
    Security: "Security improvements"

  auto_detect_category:
    rules:
      - condition: "deprecation_plan exists"
        category: "Deprecated"
      - condition: "is_bug_fix == true"
        category: "Fixed"
      - condition: "security_focus == true"
        category: "Security"
      - condition: "replaces_existing == true"
        category: "Changed"
      - default: "Added"
```

### 10.4 Serena Memory Update

**Generation**: All brownfield specs

```yaml
serena_memory_artifact:
  timing: "after spec validation passes"

  write_feature_memory:
    tool: "mcp__serena__write_memory"
    parameters:
      memory_file_name: "feature_{{SPEC_ID}}.md"
      content: |
        # Feature: {{TITLE}}

        **Spec ID**: {{SPEC_ID}}
        **Date**: {{DATE}}
        **Track**: {{TRACK}}
        **Status**: Specified

        ## Summary
        {{SUMMARY}}

        ## Affected Components
        {{#each affected_components}}
        - {{path}}: {{impact_type}}
        {{/each}}

        ## Key Decisions
        {{#each key_decisions}}
        - {{decision}}: {{rationale}}
        {{/each}}

        ## Quality Score
        - Overall: {{quality_score}}%

  update_project_history:
    tool: "mcp__serena__edit_memory"
    parameters:
      memory_file_name: "project_history.md"
      mode: "literal"
      needle: "## Recent Specs"
      repl: |
        ## Recent Specs

        - {{DATE}}: {{TITLE}} ({{SPEC_ID}}) - {{STATUS}}
```

### 10.5 Spec Registry

**Generation**: All tracks

```yaml
spec_registry_artifact:
  location: ".spec-generator/registry.json"
  mode: "append to registry"

  schema:
    spec_id: "string"
    title: "string"
    track: "quick|standard|enterprise"
    created_at: "ISO_8601"
    status: "draft|review|approved|implemented|archived"
    quality_score: "number"
    affected_components: ["string"]
    adr_number: "number|null"
    changelog_category: "string"
    author: "string"
    reviewers: ["string"]
    implementation_pr: "string|null"

  purpose: |
    Central registry for all specs enables:
    - Spec discovery and search
    - Status tracking across specs
    - Dependency analysis between specs
    - Historical trend analysis
```

### 10.6 Auggie Refresh Trigger

**Generation**: Post-implementation

```yaml
auggie_refresh_artifact:
  trigger: "spec marked as implemented"

  action:
    description: "Signal Auggie to re-index modified files"
    files: "{{implementation_files}}"
    priority: "normal"

  note: |
    Auggie maintains a real-time index. After implementation:
    1. Modified files are automatically detected
    2. Index refresh occurs on next query
    3. For large changes (>20 files), consider explicit refresh
```

### 10.7 Generation Workflow

```yaml
history_artifact_generation:
  after_validation_pass:
    - adr (standard/enterprise)
    - changelog_entry (all)
    - serena_memory_update (all brownfield)
    - spec_registry_entry (all)

  after_implementation:
    - auggie_refresh_trigger
    - serena_memory_update (status: implemented)
    - spec_registry_entry (status: implemented)

  user_confirmation:
    adr:
      prompt: "Generate ADR for this architectural decision?"
      default: true (standard/enterprise)

    changelog:
      prompt: "Add changelog entry?"
      default: true

    serena_memory:
      prompt: "Update project memory?"
      default: true (brownfield)
```

---

## 13. Command Specification

### 13.1 Command Syntax

```bash
/sc:spec [description] [options]

# Examples
/sc:spec "User authentication with OAuth2"
/sc:spec @existing-doc.md --track enterprise
/sc:spec --interactive
```

### 11.2 Options

| Option | Description | Default |
|--------|-------------|---------|
| `--track` | Force track selection | Auto-detect |
| `--interactive` | Full question flow | Based on confidence |
| `--quick` | Minimal questions | - |
| `--output` | Output path | `specs/{name}.spec.md` |
| `--format` | Output format | `markdown+yaml` |
| `--validate` | Validate only | - |
| `--score` | Show quality score | Always |
| `--brownfield` | Enable brownfield mode | Auto-detect |
| `--greenfield` | Force greenfield mode | - |
| `--skip-impact` | Skip impact analysis | - |
| `--bootstrap` | Force full agent onboarding | - |
| `--skip-bootstrap` | Skip onboarding check | - |
| `--bootstrap-depth` | Onboarding depth (quick/standard/deep) | standard |

### 11.3 Workflow Modes

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Guided** | `--interactive` | Full 3-phase question flow |
| **Smart** | Default | Ask only when confidence < 95% |
| **Quick** | `--quick` | Minimal questions, sensible defaults |
| **Validate** | `--validate` | Score existing spec |

### 11.4 Output Artifacts

```
specs/
├── feature-name.spec.md       # Human-readable specification
├── feature-name.context.yaml  # AI context block
├── feature-name.tasks.md      # Generated task list (optional)
└── feature-name.score.json    # Quality validation report

# Brownfield additions:
├── impact_analysis.json       # Impact radius and baselines (brownfield)
├── docs/adr/ADR-XXX-*.md      # Architectural decision record (standard+)
└── .spec-generator/registry.json  # Spec registry entry
```

---

## 14. Gap Analysis

### 14.1 Identified Gaps from Research

| Gap | Description | Mitigation |
|-----|-------------|------------|
| **NFR Elicitation** | Most frameworks focus on functional requirements | Add explicit NFR question category |
| **Prioritization** | Question ordering exists but not answer prioritization | Integrate MoSCoW into completion phase |
| **Conflict Resolution** | Viewpoint questions exist but conflict handling weak | Add conflict detection questions |
| **Versioning** | Initial elicitation covered but evolution not | Add "future change" question category |
| **Multi-Stakeholder** | Single-perspective bias possible | Require explicit viewpoint rotation |

### 14.2 Framework Conflicts Resolved

| Conflict | Frameworks | Resolution |
|----------|------------|------------|
| Question threshold | Clavix (95%) vs BMAD (discovery) | 95% for critical path, discovery for exploration |
| Question batching | Clavix (batch) vs Shape Up (story-flow) | Batch for efficiency, story-flow for complex |
| Output format | EARS (structured) vs Shape Up (narrative) | Generate both: narrative + EARS |
| Complexity tracks | BMAD (3 tracks) vs Kiro (per-feature) | Combine: 3 tracks with per-feature scoping |

### 14.3 Brownfield Gaps Addressed (v2.0, v2.1, v2.4)

| Gap | Description | Solution |
|-----|-------------|----------|
| **Impact Analysis** | No understanding of existing codebase context | BF-01: Auggie MCP integration |
| **Regression Risk** | No baseline capture for regression detection | BF-02: Impact analysis stage |
| **BC Questions** | Missing brownfield-specific elicitation | BF-03: Brownfield discovery questions |
| **BC Templates** | No backwards compatibility documentation | BF-04: BC template components |
| **Project History** | No ADR, changelog, memory updates | BF-05: History artifacts |
| **Quality Thresholds** | Static 80% regardless of risk | BF-06: Dynamic quality modifiers |
| **Pattern Conformance** | No validation against existing patterns | BF-07: Pattern conformance gate |
| **Fresh Agent Context** | Agent has no memory of existing brownfield project | BF-08: Agent onboarding check |
| **Reinventing the Wheel** | No research of existing solutions before speccing | BF-09: External prior art discovery |
| **Unchallenged Assumptions** | Assumptions accepted without validation or stress-testing | AVE-01: Assumption validation debates (Section 8.2) |
| **Unjustified Pattern Deviations** | Pattern deviations without structured justification | AVE-02: Pattern conformance debates (Section 8.3) |

### 14.4 Future Enhancements

1. **Multi-Model Support**: Different LLM providers for validation
2. **Collaborative Mode**: Multi-user concurrent editing
3. **Version Control Integration**: Auto-commit spec changes
4. **Template Marketplace**: Community-contributed templates
5. **Analytics Dashboard**: Track spec quality over time

---

## Appendices

### A. Source Attribution

| Source | Key Contributions |
|--------|-------------------|
| **BMAD-METHOD** | 3-track routing, agent personas, document sharding |
| **Clavix** | Confidence threshold, self-correction, template-as-runtime |
| **Kiro** | EARS notation, 3-document model, per-feature scoping |
| **Shape Up** | Appetite concept, rabbit holes, problem stories |
| **Amazon** | Five Key Questions, PR/FAQ, truth-seeking culture |
| **Google** | Non-goals, alternatives considered, trade-offs |
| **IEEE/ISO** | 6 quality attributes, RFC 2119, verifiability |
| **AI-Native** | Context blocks, agent profiling, structured schemas |

### B. Quick Reference Card

```
SPEC GENERATOR QUICK REFERENCE v2.4
====================================

TRACKS:
  Quick    (< 2 days)  → 5-8 sections
  Standard (2d-2w)     → 10-12 sections
  Enterprise (> 2w)    → 15+ sections

QUESTION PHASES:
  1. Discovery   → WHO, WHAT, WHY, SCOPE + BF-Q1-Q5 (brownfield)
  2. Validation  → ASSUMPTIONS, EVIDENCE, VIEWPOINTS
  3. Completion  → GAPS, JTBD, EARS FORMATTING

QUESTION BATCHING (v2.3):
  - Themed batches with progress indicators
  - Track caps: Quick (6), Standard (12), Enterprise (18)

QUALITY THRESHOLD (Risk-Adjusted Tiers):
  Critical (95%): Auth, payment, security, base classes 5+ consumers
  High (90%): Shared abstractions, data persistence, external APIs
  Elevated (85%): Deep dependencies (5+), 15+ files affected
  Standard (80%): Default for all other changes

AI OPTIMIZATION:
  EARS: "WHEN [x] THE SYSTEM SHALL [y] SO THAT [z]"
  RFC 2119: MUST | SHOULD | MAY | MUST NOT | SHOULD NOT
  Context Block: domain, complexity, agent_profile, quality_gates

PRIOR ART RESEARCH (BF-09):
  1. Discovery    → GitHub search for similar projects
  2. Scoring      → Trust + Relevance + Applicability
  3. Shallow scan → Find relevant files (98% reduction)
  4. Deep dive    → Auggie analysis of top 3-5 repos
  5. Debate       → Spec-panel critical evaluation
  6. Influence    → Tiered adoption (80+: Strong, 60-79: Moderate, 40-59: Reference)

BROWNFIELD MODE:
  /sc:spec "description" --brownfield
  Adds: Impact analysis, BC sections, pattern conformance, history artifacts

AGENT ONBOARDING (BF-08):
  Fresh agent? → Bootstrap workflow → Build project memories
  Stale agent? → Reconciliation workflow → Update stale memories
  Current agent? → Skip → Proceed to context acquisition

CACHING (Prior Art):
  Layer 1: Serena local (project-specific memories)
  Layer 2: Auggie cloud (semantic index, cross-project)
  Layer 3: Centralized service (FUTURE - all users/projects)

ADVERSARIAL VALIDATION (v2.4):
  Entry Points:
    1. Assumption Validation (Phase 2) - Conditional on confidence < 0.7 or assumptions > 5
    2. Pattern Conformance (BF-07) - Conditional on deviation > 0.3 or brownfield context

  Debate Modes:
    lite: 2 experts, 1 round, 5K tokens max
    standard: 4 experts, 2 rounds, 15K tokens max
    deep: 6 experts, 3 rounds, 40K tokens max

  Control Flags:
    --debate-depth [skip|lite|standard|deep]
    --debate-focus [assumptions|patterns|both|none]

  Required Outputs:
    - Traced findings: FINDING-{n}: Section {ref} → {issue} → {recommendation}
    - Test stubs: TEST-{n}: Given {context} When {action} Then {outcome}
    - Confidence delta: before/after scores

COMMAND:
  /sc:spec "description" [--track quick|standard|enterprise] [--brownfield]
  /sc:spec "description" --bootstrap              # Force fresh onboarding
  /sc:spec "description" --bootstrap-depth deep   # Thorough analysis
  /sc:spec "description" --prior-art-depth deep   # Extended prior art research
  /sc:spec "description" --skip-prior-art         # Skip prior art (not recommended)

  # Adversarial Validation (v2.4)
  /sc:spec "description" --debate-depth standard  # Set debate depth explicitly
  /sc:spec "description" --debate-focus assumptions  # Focus debates on assumptions only
  /sc:spec "description" --debate-depth skip      # Skip all adversarial debates
```

### C. Canonical Examples

> **Purpose**: Concrete examples demonstrating correct spec generation patterns for each track

#### C.1 Quick Track Example: Bug Fix Specification

```markdown
# Bug Fix: Login Timeout Error

> **Track**: Quick | **Version**: 1.0 | **Date**: 2026-01-22
> **Quality Score**: 82% | **Threshold**: 80% (Standard Risk)

## Problem Statement

WHEN users attempt to login after 15 minutes of inactivity THE SYSTEM incorrectly shows "Session expired" error SO THAT users cannot complete authentication without page refresh.

**Impact**: ~500 users/day encounter this issue (based on error logs).

## Requirements (EARS Format)

**REQ-001**: WHEN session token expires during login form submission THE SYSTEM SHALL automatically refresh the token SO THAT login completes without user intervention.

**REQ-002**: IF token refresh fails THE SYSTEM SHALL display clear error message with "Retry" button SO THAT users can recover without manual page refresh.

## Affected Components

| Component | Impact | Regression Test |
|-----------|--------|-----------------|
| `src/auth/session-manager.ts` | Modify | `tests/unit/auth/session.test.ts` |
| `src/components/LoginForm.tsx` | Extend | `tests/e2e/login.spec.ts` |

## Success Criteria

- [ ] No "Session expired" errors during normal login flow
- [ ] Token refresh happens transparently
- [ ] Error rate reduced by 95%

## AI Context Block

```yaml
domain: authentication
complexity: low
agent_profile: backend + frontend
quality_gates: [unit_test, e2e_test]
```
```

#### C.2 Standard Track Example: Brownfield Feature (OAuth Integration)

```markdown
# Feature: OAuth2 Social Login Integration

> **Track**: Standard | **Version**: 1.0 | **Date**: 2026-01-22
> **Quality Score**: 91% | **Threshold**: 90% (High Risk - Auth Flow)
> **Mode**: Brownfield

## Problem Statement

**Stakeholder Need**: SN-UX-001 - Reduce signup friction for new users

Users currently must create username/password accounts, leading to:
- 35% signup abandonment rate
- Password reset requests (20% of support tickets)
- Competitive disadvantage (competitors offer social login)

## Goals and Non-Goals

**Goals**:
- Enable login via Google, GitHub, Microsoft
- Maintain existing username/password option
- Single sign-on for returning users

**Non-Goals**:
- Replacing existing auth system (extend only)
- Supporting every OAuth provider
- Social profile data mining

## Backwards Compatibility

### Affected Components

| Component | Impact | Abstraction Level | Regression Risk |
|-----------|--------|-------------------|-----------------|
| `AuthService` | Extend | Base class | High |
| `LoginController` | Modify | User-facing API | Medium |
| `UserModel` | Extend | Data persistence | Medium |

### Preserved Behaviors

**BEHAV-001**: WHEN user submits username/password THE SYSTEM SHALL authenticate via existing flow SO THAT current users experience no change.

- **Verification**: Existing test suite passes
- **Test**: `tests/integration/auth-legacy.test.ts`

### Performance Baselines

| Endpoint | Current p50 | Current p95 | Acceptable Regression |
|----------|-------------|-------------|----------------------|
| POST /api/auth/login | 45ms | 120ms | 10% |
| GET /api/auth/session | 15ms | 35ms | 5% |

## Requirements (EARS Format)

**REQ-OAUTH-001**: WHEN user clicks "Login with Google" THE SYSTEM SHALL redirect to Google OAuth consent screen SO THAT user can authorize application access.
- **Traces to**: SN-UX-001
- **Verified by**: IT-OAUTH-001

**REQ-OAUTH-002**: WHEN OAuth provider returns authorization code THE SYSTEM SHALL exchange code for tokens and create/link user account SO THAT user gains authenticated session.
- **Traces to**: SN-UX-001
- **Verified by**: IT-OAUTH-002, UT-OAUTH-001

**REQ-OAUTH-003**: IF OAuth authentication fails THE SYSTEM SHALL display provider-specific error message with retry option SO THAT user understands failure reason.
- **Traces to**: SN-UX-001
- **Verified by**: UT-OAUTH-002

## Solution Design

[Architecture diagram, component interactions, data flow...]

## Regression Test Plan

### Unit Tests
- [ ] `tests/unit/auth/oauth-provider.test.ts` - Provider abstraction
- [ ] `tests/unit/auth/token-exchange.test.ts` - Token handling

### Integration Tests
- [ ] `tests/integration/oauth-google.test.ts` - Full Google flow
- [ ] `tests/integration/auth-legacy.test.ts` - Existing auth unchanged

### E2E Tests
- [ ] `tests/e2e/social-login.spec.ts` - User journey

## Rollback Plan

**Type**: Feature flag + database rollback

**Feature Flag**: `ENABLE_OAUTH_LOGIN`
**Disable Command**: `feature-flags set ENABLE_OAUTH_LOGIN false`
**Time to Disable**: Instant

## AI Context Block

```yaml
domain: authentication
complexity: moderate
technology: OAuth2, JWT
agent_profile: backend + security
quality_gates: [security_review, integration_test, e2e_test]
risk_tier: high
```
```

#### C.3 Deviation Example: Justified Threshold Override

```markdown
# Prototype: AI Chat Experiment

> **Track**: Quick | **Version**: 0.1 | **Date**: 2026-01-22
> **Quality Score**: 72% | **Threshold**: 80% (Standard Risk)
> **Override**: Approved | **Justification**: Time-boxed prototype (3 days)

## Override Documentation

**Calculated Threshold**: 80% (Standard Risk)
**Actual Score**: 72%
**Override Requested By**: @jane.dev
**Override Approved By**: @tech.lead

**Justification**:
This is a 3-day prototype to validate AI chat feasibility. The code:
- Will NOT go to production
- Is isolated in `experiments/` directory
- Has explicit expiration date (delete after 2026-02-01)
- Serves only to inform go/no-go decision

**Accepted Risks**:
- No comprehensive error handling (acceptable for prototype)
- Limited test coverage (acceptable for throwaway code)
- No backwards compatibility section (greenfield experiment)

**Conditions**:
- [ ] Code deleted by 2026-02-01 if not productionized
- [ ] Full spec required if moving to production
- [ ] No production dependencies on this code

## Problem Statement

Evaluate whether GPT-4 integration can reduce support ticket volume by auto-responding to common questions.

## Success Criteria

- [ ] Prototype responds to 5 sample queries
- [ ] Response latency < 3s
- [ ] Team can evaluate feasibility

---
*Note: This spec demonstrates valid threshold override with proper documentation.*
```

#### C.4 When to Deviate from Standards

| Scenario | Deviation Allowed | Required Documentation |
|----------|-------------------|----------------------|
| Time-boxed prototype | Yes | Expiration date, delete commitment |
| Internal tooling | Yes | Limited audience acknowledgment |
| Hotfix/emergency | Yes | Post-incident full spec commitment |
| Production feature | **No** | Must meet threshold or iterate |
| Security-related | **No** | Must meet or exceed threshold |
| External API | **No** | Full spec required |

---

*Generated: 2026-01-22 | Version: 2.3.0 | Status: DRAFT*
*Sources: 7+ frameworks, 100+ research files, comprehensive synthesis*
*v2.0: Brownfield development support (BF-01 through BF-07)*
*v2.1: Agent onboarding (BF-08), Prior art discovery (BF-09)*
*v2.3: Risk-adjusted thresholds, question batching, requirements traceability, operability rebalancing*
*v2.4: Adversarial Validation Engine (SpecDebateEngine) with conditional debates*
