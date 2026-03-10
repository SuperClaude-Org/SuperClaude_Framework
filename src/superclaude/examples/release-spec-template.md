# Release Spec Template

> **Usage**: Copy this template when creating a new release specification. Fill in all `{{SC_PLACEHOLDER:*}}` values. Remove sections marked `[CONDITIONAL: ...]` if not applicable to your spec type. Delete this usage block from your final spec.
>
> **Spec types supported**: New feature, refactoring, portification, infrastructure
>
> **Conditional sections by spec type**:
> - **Portification**: Include Section 9 (Migration & Rollout), Section 5 (Interface Contracts)
> - **Refactoring**: Include Section 4.3 (Removed Files), Section 9 (Migration & Rollout)
> - **New feature**: Include Section 4.5 (Data Models), Section 5.1 (CLI Surface)
> - **Infrastructure**: Include Section 5.3 (Phase Contracts), Section 8.3 (Manual/E2E Tests)
>
> **Quality gate**: Before this spec is considered complete, it should pass `/sc:spec-panel --focus correctness,architecture` and `/sc:spec-panel --mode critique`.
>
> **Sentinel self-check**: After populating, verify zero remaining sentinels: `grep -c '{{SC_PLACEHOLDER:' <output-file>` should return 0.

---

```yaml
---
title: "{{SC_PLACEHOLDER:spec_title}}"
version: "1.0.0"
status: draft
feature_id: {{SC_PLACEHOLDER:fr_id}}
parent_feature: {{SC_PLACEHOLDER:parent_feature_or_null}}
spec_type: {{SC_PLACEHOLDER:new_feature_or_refactoring_or_portification_or_infrastructure}}
complexity_score: {{SC_PLACEHOLDER:0.0_to_1.0}}
complexity_class: {{SC_PLACEHOLDER:simple_or_moderate_or_high}}
target_release: {{SC_PLACEHOLDER:version}}
authors: [user, claude]
created: {{SC_PLACEHOLDER:yyyy_mm_dd}}
quality_scores:
  clarity: {{SC_PLACEHOLDER:0.0_to_10.0}}
  completeness: {{SC_PLACEHOLDER:0.0_to_10.0}}
  testability: {{SC_PLACEHOLDER:0.0_to_10.0}}
  consistency: {{SC_PLACEHOLDER:0.0_to_10.0}}
  overall: {{SC_PLACEHOLDER:0.0_to_10.0}}
---
```

## 1. Problem Statement

> What problem does this work solve? Why does it matter? What fails or is suboptimal today?

{{SC_PLACEHOLDER:problem_description}}

### 1.1 Evidence

> Concrete evidence that the problem exists. Links to issues, failing tests, user reports, forensic findings.

| Evidence | Source | Impact |
|----------|--------|--------|
| {{SC_PLACEHOLDER:evidence_1}} | {{SC_PLACEHOLDER:source}} | {{SC_PLACEHOLDER:impact}} |

### 1.2 Scope Boundary

> What this spec addresses and explicitly does NOT address.

**In scope**: {{SC_PLACEHOLDER:in_scope}}

**Out of scope**: {{SC_PLACEHOLDER:out_of_scope}}

## 2. Solution Overview

> High-level description of the approach. What changes, what stays the same.

{{SC_PLACEHOLDER:solution_overview}}

### 2.1 Key Design Decisions

> Decisions made during brainstorming/design that shaped this spec. Each decision should have a rationale.

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| {{SC_PLACEHOLDER:decision_1}} | {{SC_PLACEHOLDER:choice}} | {{SC_PLACEHOLDER:alternatives}} | {{SC_PLACEHOLDER:rationale}} |

### 2.2 Workflow / Data Flow

> How the system works end-to-end after this change. Use ASCII diagrams for pipeline flows.

```
{{SC_PLACEHOLDER:flow_diagram}}
```

## 3. Functional Requirements

> Numbered requirements. Each must be testable and traceable.

### FR-{{SC_PLACEHOLDER:id}}.1: {{SC_PLACEHOLDER:requirement_title}}

**Description**: {{SC_PLACEHOLDER:what_it_does}}

**Acceptance Criteria**:
- [ ] {{SC_PLACEHOLDER:criterion_1}}
- [ ] {{SC_PLACEHOLDER:criterion_2}}

**Dependencies**: {{SC_PLACEHOLDER:dependencies_or_none}}

### FR-{{SC_PLACEHOLDER:id}}.2: {{SC_PLACEHOLDER:requirement_title}}

{{SC_PLACEHOLDER:repeat_pattern}}

## 4. Architecture

### 4.1 New Files

> Files created by this work. Include purpose and dependencies.

| File | Purpose | Dependencies |
|------|---------|-------------|
| {{SC_PLACEHOLDER:file_path}} | {{SC_PLACEHOLDER:purpose}} | {{SC_PLACEHOLDER:deps}} |

### 4.2 Modified Files

> Existing files changed. Include nature of change.

| File | Change | Rationale |
|------|--------|-----------|
| {{SC_PLACEHOLDER:file_path}} | {{SC_PLACEHOLDER:change_description}} | {{SC_PLACEHOLDER:why}} |

### 4.3 Removed Files [CONDITIONAL: refactoring, portification]

> Files or sections removed. Include migration notes.

| File/Section | Reason | Migration |
|-------------|--------|-----------|
| {{SC_PLACEHOLDER:target}} | {{SC_PLACEHOLDER:reason}} | {{SC_PLACEHOLDER:migration_notes}} |

### 4.4 Module Dependency Graph

```
{{SC_PLACEHOLDER:dependency_diagram}}
```

### 4.5 Data Models [CONDITIONAL: new_feature, portification]

> New or modified data structures. Include field definitions.

```python
{{SC_PLACEHOLDER:data_model_code}}
```

### 4.6 Implementation Order

> Dependency-respecting order for implementation. Include parallelization opportunities.

```
1. {{SC_PLACEHOLDER:first_step}}     -- {{SC_PLACEHOLDER:rationale}}
2. {{SC_PLACEHOLDER:second_step}}    -- {{SC_PLACEHOLDER:rationale}}
   {{SC_PLACEHOLDER:parallel_step}}  -- [parallel with step 2]
3. {{SC_PLACEHOLDER:third_step}}     -- depends on 1, 2
```

## 5. Interface Contracts [CONDITIONAL: portification, new_feature]

> API contracts, gate criteria, prompt specifications, CLI surface changes.

### 5.1 CLI Surface [CONDITIONAL: new_feature, portification]

```
{{SC_PLACEHOLDER:cli_usage}}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| {{SC_PLACEHOLDER:option}} | {{SC_PLACEHOLDER:type}} | {{SC_PLACEHOLDER:default}} | {{SC_PLACEHOLDER:desc}} |

### 5.2 Gate Criteria [CONDITIONAL: portification]

> For pipeline-based work. Define validation gates.

| Step | Gate Tier | Frontmatter | Min Lines | Semantic Checks |
|------|-----------|-------------|-----------|-----------------|
| {{SC_PLACEHOLDER:step}} | {{SC_PLACEHOLDER:tier}} | {{SC_PLACEHOLDER:fields}} | {{SC_PLACEHOLDER:n}} | {{SC_PLACEHOLDER:checks}} |

### 5.3 Phase Contracts [CONDITIONAL: portification, infrastructure]

> For multi-phase workflows. Define inter-phase contracts.

```yaml
{{SC_PLACEHOLDER:contract_schema}}
```

## 6. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-{{SC_PLACEHOLDER:id}}.1 | {{SC_PLACEHOLDER:requirement}} | {{SC_PLACEHOLDER:target}} | {{SC_PLACEHOLDER:how_measured}} |

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| {{SC_PLACEHOLDER:risk_1}} | {{SC_PLACEHOLDER:low_med_high}} | {{SC_PLACEHOLDER:low_med_high}} | {{SC_PLACEHOLDER:mitigation}} |

## 8. Test Plan

### 8.1 Unit Tests

| Test | File | Validates |
|------|------|-----------|
| {{SC_PLACEHOLDER:test_name}} | {{SC_PLACEHOLDER:file_path}} | {{SC_PLACEHOLDER:what_it_validates}} |

### 8.2 Integration Tests

| Test | Validates |
|------|-----------|
| {{SC_PLACEHOLDER:test_name}} | {{SC_PLACEHOLDER:what_it_validates}} |

### 8.3 Manual / E2E Tests [CONDITIONAL: infrastructure, portification]

| Scenario | Steps | Expected Outcome |
|----------|-------|-----------------|
| {{SC_PLACEHOLDER:scenario}} | {{SC_PLACEHOLDER:steps}} | {{SC_PLACEHOLDER:expected}} |

## 9. Migration & Rollout [CONDITIONAL: refactoring, portification]

> How to transition from current state to new state. Breaking changes, backwards compatibility.

- **Breaking changes**: {{SC_PLACEHOLDER:yes_no_details}}
- **Backwards compatibility**: {{SC_PLACEHOLDER:strategy}}
- **Rollback plan**: {{SC_PLACEHOLDER:plan}}

## 10. Downstream Inputs

> What this spec feeds into. How downstream consumers (sc:roadmap, sc:tasklist, etc.) use the output.

### For sc:roadmap
{{SC_PLACEHOLDER:themes_and_milestones}}

### For sc:tasklist
{{SC_PLACEHOLDER:task_breakdown_guidance}}

## 11. Open Items

> Unresolved questions. Each should have an owner and deadline. Empty section means all questions resolved.

| Item | Question | Impact | Resolution Target |
|------|----------|--------|-------------------|
| {{SC_PLACEHOLDER:item}} | {{SC_PLACEHOLDER:question}} | {{SC_PLACEHOLDER:impact}} | {{SC_PLACEHOLDER:target}} |

## 12. Brainstorm Gap Analysis

> Auto-populated by `sc:cli-portify` Phase 3c embedded brainstorm pass. For manually created specs, use `/sc:brainstorm` to identify gaps.

| Gap ID | Description | Severity | Affected Section | Persona |
|--------|-------------|----------|-----------------|---------|
| {{SC_PLACEHOLDER:gap_id}} | {{SC_PLACEHOLDER:description}} | {{SC_PLACEHOLDER:high_medium_low}} | {{SC_PLACEHOLDER:affected_section}} | {{SC_PLACEHOLDER:persona}} |

{{SC_PLACEHOLDER:gap_analysis_summary}}

---

## Appendix A: Glossary [CONDITIONAL: all types -- include if domain-specific terminology used]

| Term | Definition |
|------|-----------|
| {{SC_PLACEHOLDER:term}} | {{SC_PLACEHOLDER:definition}} |

## Appendix B: Reference Documents [CONDITIONAL: all types -- include if external references needed]

| Document | Relevance |
|----------|-----------|
| {{SC_PLACEHOLDER:doc_path}} | {{SC_PLACEHOLDER:why_relevant}} |
