# Release Spec Template

> **Usage**: Copy this template when creating a new release specification. Fill in all `{PLACEHOLDER}` values. Remove sections marked `[CONDITIONAL]` if not applicable. Delete this usage block from your final spec.
>
> **Spec types supported**: New feature, refactoring, portification, infrastructure
>
> **Quality gate**: Before this spec is considered complete, it should pass `/sc:spec-panel --focus correctness,architecture` and `/sc:spec-panel --mode critique`.

---

```yaml
---
title: "{SPEC_TITLE}"
version: "1.0.0"
status: draft
feature_id: {FR_ID}
parent_feature: {PARENT_FEATURE_OR_NULL}
spec_type: {new_feature|refactoring|portification|infrastructure}
complexity_score: {0.0-1.0}
complexity_class: {simple|moderate|high}
target_release: {VERSION}
authors: [user, claude]
created: {YYYY-MM-DD}
---
```

## 1. Problem Statement

> What problem does this work solve? Why does it matter? What fails or is suboptimal today?

{PROBLEM_DESCRIPTION}

### 1.1 Evidence

> Concrete evidence that the problem exists. Links to issues, failing tests, user reports, forensic findings.

| Evidence | Source | Impact |
|----------|--------|--------|
| {EVIDENCE_1} | {SOURCE} | {IMPACT} |

### 1.2 Scope Boundary

> What this spec addresses and explicitly does NOT address.

**In scope**: {IN_SCOPE}

**Out of scope**: {OUT_OF_SCOPE}

## 2. Solution Overview

> High-level description of the approach. What changes, what stays the same.

{SOLUTION_OVERVIEW}

### 2.1 Key Design Decisions

> Decisions made during brainstorming/design that shaped this spec. Each decision should have a rationale.

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| {DECISION_1} | {CHOICE} | {ALTERNATIVES} | {RATIONALE} |

### 2.2 Workflow / Data Flow

> How the system works end-to-end after this change. Use ASCII diagrams for pipeline flows.

```
{FLOW_DIAGRAM}
```

## 3. Functional Requirements

> Numbered requirements. Each must be testable and traceable.

### FR-{ID}.1: {REQUIREMENT_TITLE}

**Description**: {WHAT_IT_DOES}

**Acceptance Criteria**:
- [ ] {CRITERION_1}
- [ ] {CRITERION_2}

**Dependencies**: {DEPENDENCIES_OR_NONE}

### FR-{ID}.2: {REQUIREMENT_TITLE}

{REPEAT_PATTERN}

## 4. Architecture

### 4.1 New Files

> Files created by this work. Include purpose and dependencies.

| File | Purpose | Dependencies |
|------|---------|-------------|
| {FILE_PATH} | {PURPOSE} | {DEPS} |

### 4.2 Modified Files

> Existing files changed. Include nature of change.

| File | Change | Rationale |
|------|--------|-----------|
| {FILE_PATH} | {CHANGE_DESCRIPTION} | {WHY} |

### 4.3 Removed Files [CONDITIONAL]

> Files or sections removed. Include migration notes.

| File/Section | Reason | Migration |
|-------------|--------|-----------|
| {TARGET} | {REASON} | {MIGRATION_NOTES} |

### 4.4 Module Dependency Graph

```
{DEPENDENCY_DIAGRAM}
```

### 4.5 Data Models [CONDITIONAL]

> New or modified data structures. Include field definitions.

```python
{DATA_MODEL_CODE}
```

### 4.6 Implementation Order

> Dependency-respecting order for implementation. Include parallelization opportunities.

```
1. {FIRST_STEP}     — {RATIONALE}
2. {SECOND_STEP}    — {RATIONALE}
   {PARALLEL_STEP}  — [parallel with step 2]
3. {THIRD_STEP}     — depends on 1, 2
```

## 5. Interface Contracts [CONDITIONAL]

> API contracts, gate criteria, prompt specifications, CLI surface changes.

### 5.1 CLI Surface [CONDITIONAL]

```
{CLI_USAGE}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| {OPTION} | {TYPE} | {DEFAULT} | {DESC} |

### 5.2 Gate Criteria [CONDITIONAL]

> For pipeline-based work. Define validation gates.

| Step | Gate Tier | Frontmatter | Min Lines | Semantic Checks |
|------|-----------|-------------|-----------|-----------------|
| {STEP} | {TIER} | {FIELDS} | {N} | {CHECKS} |

### 5.3 Phase Contracts [CONDITIONAL]

> For multi-phase workflows. Define inter-phase contracts.

```yaml
{CONTRACT_SCHEMA}
```

## 6. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-{ID}.1 | {REQUIREMENT} | {TARGET} | {HOW_MEASURED} |

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| {RISK_1} | {LOW/MED/HIGH} | {LOW/MED/HIGH} | {MITIGATION} |

## 8. Test Plan

### 8.1 Unit Tests

| Test | File | Validates |
|------|------|-----------|
| {TEST_NAME} | {FILE_PATH} | {WHAT_IT_VALIDATES} |

### 8.2 Integration Tests

| Test | Validates |
|------|-----------|
| {TEST_NAME} | {WHAT_IT_VALIDATES} |

### 8.3 Manual / E2E Tests [CONDITIONAL]

| Scenario | Steps | Expected Outcome |
|----------|-------|-----------------|
| {SCENARIO} | {STEPS} | {EXPECTED} |

## 9. Migration & Rollout

> How to transition from current state to new state. Breaking changes, backwards compatibility.

- **Breaking changes**: {YES_NO_DETAILS}
- **Backwards compatibility**: {STRATEGY}
- **Rollback plan**: {PLAN}

## 10. Downstream Inputs

> What this spec feeds into. How downstream consumers (sc:roadmap, sc:tasklist, etc.) use the output.

### For sc:roadmap
{THEMES_AND_MILESTONES}

### For sc:tasklist
{TASK_BREAKDOWN_GUIDANCE}

## 11. Open Items

> Unresolved questions. Each should have an owner and deadline. Empty section means all questions resolved.

| Item | Question | Impact | Resolution Target |
|------|----------|--------|-------------------|
| {ITEM} | {QUESTION} | {IMPACT} | {TARGET} |

---

## Appendix A: Glossary [CONDITIONAL]

| Term | Definition |
|------|-----------|
| {TERM} | {DEFINITION} |

## Appendix B: Reference Documents [CONDITIONAL]

| Document | Relevance |
|----------|-----------|
| {DOC_PATH} | {WHY_RELEVANT} |
