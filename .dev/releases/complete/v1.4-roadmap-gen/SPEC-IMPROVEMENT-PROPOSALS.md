# SC-ROADMAP-FEATURE-SPEC Improvement Proposals v1.0

**Generated**: 2026-01-26
**Process**: `/sc:reflect` + `/sc:spawn` adversarial debate with steelmanning protocol
**Status**: Validated - Ready for Implementation

---

## Executive Summary

| Proposal | Type | Verdict | Confidence | Complexity | Impact |
|----------|------|---------|------------|------------|--------|
| P1: Declarative Parallelization | Weakness Fix | MODIFY | 82% | Low | High |
| P2: Inline Template Algorithm | Weakness Fix | MODIFY | 82% | Medium | High |
| P3: Wave Parallelization Strategy | Improvement | MODIFY | 81% | Low | High |
| P4: Keyword Precedence | Improvement | MODIFY→CONSOLIDATE | 85% | Low | Medium |

**All proposals approved with modifications. No conflicts detected between proposals.**

---

## Proposal P1: Declarative Dependency Syntax for Wave Steps

### Problem
Section 3.4 (Wave 3 Generation) lists steps sequentially without parallelization guidance, violating RULES.md "Parallel Everything" principle.

### Original Proposal
Add `parallel_group_N` positional groupings.

### Debate Outcome: MODIFY
- **Factual error identified**: Original example incorrectly placed `extraction.md` in Wave 3 (it's a Wave 1 output)
- **Better approach**: Declarative dependency syntax with explicit `concurrent_with` markers

### Approved Implementation

Add to Section 3.4:

```yaml
wave_3_generation:
  dependency_model:
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
    parallel_eligible: "Steps with matching concurrent_with can execute together"
    error_behavior: "Fail-isolated with rollback capability"
    framework_reference: "Implements RULES.md 'Batch Operations' (Priority: CRITICAL)"
```

### Cross-Section Impact
- **Section 5.1**: No conflict - MCP assignments remain unchanged
- **Section 7.1**: No conflict - Artifact list unchanged
- **Section 11.2**: Supports performance targets with realistic 30-45% gains

---

## Proposal P2: Inline Template Generation Algorithm

### Problem
Section 3.3 step 4 says "Generate variant from domain analysis" with zero specification.

### Original Proposal
Add Section 3.3.1 with fixed milestone counts (3/5/7).

### Debate Outcome: MODIFY
- **Fixed counts conflict**: Real-world evidence shows flexibility needed (6 milestones observed for complexity 0.85)
- **Missing multi-domain resolution**: No handling for co-primary domains
- **Incomplete required sections**: Missing Type, Priority, Files Affected, Risk Level

### Approved Implementation

Add Section 3.3.1:

```yaml
3.3.1 Inline Template Generation Algorithm

When no matching template is found:

milestone_count_formula:
  complexity < 0.4:
    range: 3-4 milestones
    base_names: [Foundation, Implementation, Validation]
  complexity 0.4-0.7:
    range: 4-6 milestones
    base_names: [Foundation, Design, Implementation, Testing, Deployment]
  complexity > 0.7:
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
  - Acceptance Criteria: "Testable statements, minimum 1"
  - Risk Level: "High | Medium | Low"
  - Files Affected: "List of predicted paths, or 'TBD' if unknown"

minimum_requirements:
  - Template MUST include at least 1 milestone
  - Each milestone MUST have at least 1 deliverable
  - extraction.md MUST contain at least 3 requirements

input_clarification:
  complexity_score:
    source: "Output of step_4_complexity_scoring (Section 3.2)"
    scale: "0.0-1.0 (normalized)"
    conversion_rule: "If consuming from 0-100 scale, divide by 100"
```

### Cross-Section Impact
- **Section 3.2**: Aligns with existing complexity scoring factors
- **Section 4.1**: Multi-primary handling aligns with persona activation thresholds (>=40%)
- **Section 7.1**: Required sections now match tasklist file structure
- **Appendix D**: Example should be updated to show new required sections

---

## Proposal P3: Section 3.7 Parallelization Strategy

### Problem
Wave parallelization opportunities are implicit throughout Section 3.

### Original Proposal
Add Section 3.7 consolidating all parallelization guidance.

### Debate Outcome: MODIFY
- **Performance expectations optimistic**: Adjust from 40-60% to 30-45% reduction
- **Wave 4 constraint**: Task tool AWAIT semantics require sequential execution
- **Missing error handling**: Need parallel failure semantics

### Approved Implementation

Add Section 3.7:

```yaml
3.7 Parallelization Strategy

This section consolidates parallel execution opportunities across all waves.

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
  step_dependencies:
    roadmap → tasklists → [test-strategy, execution-prompt]
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
  without_parallelization: 3-5 minutes
  with_parallelization: 1.5-3 minutes (30-45% reduction)
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

### Cross-Section Impact
- **Section 3.4**: Dependency model (P1) provides step-level detail; Section 3.7 provides wave-level strategy
- **Section 5.1**: MCP assignments unchanged; fallback behavior documented in MCP.md
- **Section 11.2**: Performance targets now achievable with realistic 30-45% gains

---

## Proposal P4: Keyword Precedence Consolidation

### Problem
Conflicting tier keywords lack explicit precedence rules.

### Original Proposal
Add Section 9.2 with keyword weights and compound phrase wildcards.

### Debate Outcome: MODIFY → CONSOLIDATE
- **Conflicts with ORCHESTRATOR.md**: Would create duplicate source of truth
- **Wildcards not supported**: Current implementation uses substring matching
- **Intra-tier weights add complexity without benefit**: All STRICT keywords trigger same verification

### Approved Implementation

**DO NOT add Section 9.2**. Instead, add clarifying note to Section 9.1:

```yaml
# Add to Section 9.1 after the tier table:

tier_classification_pipeline:
  step_1: "Check user override (--compliance flag)"
  step_2: "Check compound phrase detection (ORCHESTRATOR.md Section 'Compound Phrase Overrides')"
  step_3: "Check EXEMPT pattern matching (regex patterns for read-only verbs)"
  step_4: "Score keywords by tier"
  step_5: "Apply context boosters (file count, security paths)"
  step_6: "Resolve conflicts using tier priority: STRICT > EXEMPT > LIGHT > STANDARD"

reference_note: |
  Compound phrase definitions and conflict resolution examples are maintained in
  ORCHESTRATOR.md to ensure single source of truth. Key rules:
  - "quick fix" → LIGHT (compound overrides "fix")
  - "fix security" → STRICT (security always escalates)
  - "explain [verb pattern]" → EXEMPT (read-only verbs bypass scoring)
```

### Cross-Section Impact
- **ORCHESTRATOR.md**: Remains single source of truth for compound phrases
- **Section 6.1**: No conflict with critical corrections table
- **Section 8.1**: Error handling for ambiguous classification can reference pipeline

---

## Conflict Analysis

### Cross-Proposal Compatibility Matrix

| Proposal | P1 | P2 | P3 | P4 |
|----------|----|----|----|----|
| P1 (Dependencies) | - | ✅ No conflict | ✅ Complementary | ✅ No interaction |
| P2 (Templates) | ✅ No conflict | - | ✅ No interaction | ✅ No interaction |
| P3 (Parallelization) | ✅ Complementary | ✅ No interaction | - | ✅ No interaction |
| P4 (Keywords) | ✅ No interaction | ✅ No interaction | ✅ No interaction | - |

**P1 + P3 Complementary**: P1 provides step-level dependency syntax; P3 provides wave-level strategy. They work together without overlap.

### Convention Compliance Check

| Convention | P1 | P2 | P3 | P4 |
|------------|----|----|----|----|
| YAML format consistency | ✅ | ✅ | ✅ | ✅ |
| Section numbering scheme | ✅ 3.4 update | ✅ New 3.3.1 | ✅ New 3.7 | ✅ 9.1 update |
| Cross-reference style | ✅ | ✅ | ✅ | ✅ |
| Framework alignment | ✅ RULES.md | ✅ PERSONAS.md | ✅ RULES.md | ✅ ORCHESTRATOR.md |

**All proposals pass convention compliance.**

---

## Implementation Order

Recommended implementation sequence:

1. **P2 (Template Algorithm)** - Foundation for template discovery
2. **P1 (Dependency Syntax)** - Required before P3
3. **P3 (Parallelization Strategy)** - Depends on P1 step definitions
4. **P4 (Keyword Clarification)** - Independent, can be done anytime

---

## Files to Modify

| File | Changes |
|------|---------|
| `SC-ROADMAP-FEATURE-SPEC.md` | Add Section 3.3.1, update Section 3.4, add Section 3.7, update Section 9.1 |
| `Appendix D` | Update examples to reflect new required sections |

**No other spec files require modification.**

---

*Generated via /sc:reflect + /sc:spawn adversarial debate process*
*Steelmanning protocol applied to all proposals*
*Quality score: 82% average confidence across debates*
