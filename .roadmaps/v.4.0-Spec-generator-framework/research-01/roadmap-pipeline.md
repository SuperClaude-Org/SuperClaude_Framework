# Roadmap Pipeline Interface Research

> **Source**: IBOpenCode Roadmap Generator (v.4.1-roadmap-gen)
> **Researched**: 2026-01-17
> **Purpose**: Define interface contract between spec-panel output and roadmap generator input

---

## Executive Summary

The IBOpenCode Roadmap Generator transforms specification documents into deterministic, file-driven release roadmap packages. This research documents the exact input format, ID schemes, metadata requirements, and pipeline phases to enable seamless integration between spec-panel output and roadmap generator input.

---

## 1. Input Format Requirements

### 1.1 Input Contract

The roadmap generator expects a **single specification file** (markdown) with the following characteristics:

| Aspect | Requirement |
|--------|-------------|
| Format | Markdown (`.md`) file |
| Content | Must contain actionable items (not empty/placeholder) |
| Structure | Requirements, features, bugs, improvements, docs, refactoring items |
| Path | Must be provided by user (file must exist and be accessible) |

### 1.2 Actionable Item Detection

The generator extracts "discrete objectives, requirements, issues, or improvements" that can be:
- Feature requests
- Bug fixes
- Performance improvements
- Refactoring tasks
- Documentation needs

**Invalid inputs that cause STOP:**
- Missing/inaccessible file path
- Empty or placeholder-only content
- No actionable items detected

---

## 2. ID Scheme

### 2.1 ID Prefix Mapping

| ID Prefix | Item Type | Table Display Type |
|-----------|-----------|-------------------|
| `REQ-###` | Requirements/Features | `FEATURE` |
| `BUG-###` | Bug fixes | `BUGFIX` |
| `IMP-###` | Improvements/Optimizations | `IMPROVEMENT` |
| `REF-###` | Refactoring | `REFACTOR` |
| `DOC-###` | Documentation | `DOC` |

### 2.2 ID Assignment Rules

1. **Sequential numbering**: IDs are assigned sequentially per prefix (REQ-001, REQ-002, ...)
2. **Deterministic ordering**: Preserve order of first appearance in input document
3. **Unique IDs**: Each item gets exactly one unique ID
4. **No bundling**: Avoid combining unrelated work into one item

### 2.3 Analysis-to-Implementation ID Mapping

When converting analysis findings to implementation items (bridge specification pattern):

| Analysis ID Type | Maps To | Implementation Type |
|------------------|---------|---------------------|
| `DEAD-###` | `REF-###` | REFACTOR |
| `DISC-###` (discrepancy) | `BUG-###` or `DOC-###` | BUGFIX or DOC |
| `UNDOC-###` (undocumented) | `DOC-###` | DOC |
| `DEPR-###` (deprecated) | `REF-###` or `IMP-###` | REFACTOR or IMPROVEMENT |
| `ORPH-###` (orphaned files) | `REF-###` | REFACTOR |

---

## 3. Required Metadata/Fields Per Item

### 3.1 Extraction Table Schema

Each extracted item must have these fields:

| Field | Required | Description | Valid Values |
|-------|----------|-------------|--------------|
| `ID` | Yes | Unique identifier | `REQ-###`, `BUG-###`, `IMP-###`, `REF-###`, `DOC-###` |
| `Type` | Yes | Item classification | `FEATURE`, `BUGFIX`, `IMPROVEMENT`, `REFACTOR`, `DOC` |
| `Domain` | Yes | Technical domain | See domain enum below |
| `Description` | Yes | Clear, actionable description | Free text |
| `Dependencies` | Yes | Related item IDs | `None`, `TBD`, or comma-separated IDs |
| `Priority` | Yes | Urgency level | `P0-Critical`, `P1-High`, `P2-Medium` (default), `P3-Low` |

### 3.2 Domain Enum

| Domain | Description |
|--------|-------------|
| `FRONTEND` | UI components, client-side logic |
| `BACKEND` | Server-side, API implementation |
| `DEVOPS` | CI/CD, deployment, infrastructure |
| `SECURITY` | Authentication, authorization, vulnerabilities |
| `ARCHITECTURE` | System design, patterns, structure |
| `DOCS` | Documentation, guides, readmes |
| `API` | REST/GraphQL endpoint changes, API contracts, versioning |
| `CONFIG` | Environment configuration, build settings |
| `TESTING` | Test infrastructure, utilities, coverage |

### 3.3 Priority Enum

| Priority | Description | Default |
|----------|-------------|---------|
| `P0-Critical` | Immediate action required | No |
| `P1-High` | High urgency | No |
| `P2-Medium` | Standard priority | **Yes** (if not specified) |
| `P3-Low` | Low priority | No |

---

## 4. Pipeline Process (6 Core Phases + Extensions)

### 4.1 Core 6-Phase Pipeline (v2.1 Prompt)

| Phase | Name | Description | Output |
|-------|------|-------------|--------|
| **Preflight** | Validation | Verify input exists, is actionable, output dir available | Pass/Fail gate |
| **Phase 1** | Input Extraction | Parse specification, assign IDs, normalize types, identify dependencies | `extraction.md` |
| **Phase 2** | Persona Selection | Calculate domain distribution, select primary (>40%) and consulting (>15%) personas | Documented in roadmap metadata |
| **Phase 3** | Roadmap Construction | Transform items into dependency-ordered milestones with acceptance criteria | `roadmap.md` |
| **Phase 4** | Test Strategy | Create test plan mapping deliverables to unit/integration/acceptance/regression | `test-strategy.md` |
| **Phase 5** | Execution Prompt | Generate self-contained execution guide for implementation | `execution-prompt.md` |
| **Phase 6** | Self-Validation | Verify artifact completeness, traceability, schema compliance | Validation report |

### 4.2 Extended 9-Phase Pipeline (v3.0 Spec)

The v3.0 specification adds these phases:

| Phase | Name | Description | Output |
|-------|------|-------------|--------|
| **Phase 2.5** | Template Evaluation | Score templates against extraction+persona, select or create variant | `template-selection.md` |
| **Phase 7** | Content Upgrade | Invoke crossLLM for artifact improvement (parallel) | Upgraded artifacts |
| **Phase 7.5** | Consistency Validation | Verify upgraded artifacts remain internally consistent | `consistency-report.md` |

### 4.3 Phase Gate Requirements

**Between Phase 1 and 2:**
> PAUSE for user confirmation: "Extraction complete. [N] items identified. Review `.roadmaps/[version]/extraction.md` before proceeding?"

**Between Phase 3 and 4:**
> PAUSE for user confirmation: "Roadmap construction complete. [N] milestones with [M] total deliverables."

**Between Phase 4 and 5:**
> PAUSE for user confirmation: "Test strategy complete. [N] deliverables mapped to test coverage."

---

## 5. Output Artifacts

### 5.1 Required Artifacts (4 Core)

All artifacts written under `.roadmaps/[version]/`:

| Artifact | Description | Key Sections |
|----------|-------------|--------------|
| `extraction.md` | Normalized extraction table | ID, Type, Domain, Description, Dependencies, Priority |
| `roadmap.md` | Dependency-ordered milestones | Metadata, Executive Summary, Milestones, Dependency Graph, Risk Register |
| `test-strategy.md` | Test coverage matrix | Test Environment, Test Matrix, Execution Order, Coverage Targets |
| `execution-prompt.md` | Implementation guide | Context Loading, Execution Rules, Task Pattern, Checkpoints, Stop Conditions |

### 5.2 Additional Artifacts (Extended Pipeline)

| Artifact | Phase | Description |
|----------|-------|-------------|
| `template-selection.md` | 2.5 | Template scoring rationale |
| `upgrade-log.md` | 7 | crossLLM upgrade results |
| `consistency-report.md` | 7.5 | Cross-artifact validation findings |
| `*.draft.md` | 7 | Pre-upgrade artifact copies |

### 5.3 Roadmap.md Schema

```markdown
# Release Roadmap: [VERSION] - [RELEASE_NAME]

## Metadata
- **Source Specification**: [absolute path to input file]
- **Generated**: [ISO 8601 timestamp]
- **Generator Version**: v2.1
- **Primary Persona**: [persona with rationale]
- **Codebase State**: [git commit hash if applicable, else N/A]
- **Item Count**: [X] features, [Y] bugs, [Z] improvements, [A] refactors, [B] docs

## Executive Summary
[2-3 sentences: What this release accomplishes and key outcomes]

## Milestones Overview
| Milestone | Name | Deliverables | Dependencies | Risk Level |
|-----------|------|--------------|--------------|------------|

---

### Milestone 1: [NAME]
**Objective**: [What completing this milestone achieves]
**Dependencies**: [Prior milestones or external deps]
**Estimated Complexity**: [Low | Medium | High]

#### Deliverables
| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|

#### Verification Checkpoint M1
- [ ] All deliverables code-complete
- [ ] Unit tests written and passing
- [ ] Integration verified
- [ ] No regressions
- [ ] Documentation updated

[REPEAT FOR EACH MILESTONE]

---

## Dependency Graph
[Textual representation using IDs]

## Risk Register
| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
```

### 5.4 Extraction.md Schema

```markdown
# Extraction: [VERSION]

> **Source**: [path to input file]
> **Generated**: [date]
> **Generator Version**: v2.0

## Extracted Items

| ID | Type | Domain | Description | Dependencies | Priority |
|----|------|--------|-------------|--------------|----------|
| REQ-001 | FEATURE | BACKEND | ... | None | P1-High |
| BUG-001 | BUGFIX | FRONTEND | ... | REQ-001 | P0-Critical |

## Summary

| Type | Count | Percentage |
|------|-------|------------|
| FEATURE | 20 | 64.5% |
| DOC | 5 | 16.1% |

## Domain Distribution

| Domain | Count | Percentage |
|--------|-------|------------|
| BACKEND | 17 | 54.8% |
| FRONTEND | 8 | 25.8% |
```

---

## 6. Interface Contract: Spec-Panel to Roadmap Generator

### 6.1 Spec-Panel Output Requirements

For seamless integration, spec-panel output should include:

```markdown
# Implementation Specification: [PROJECT] - [SCOPE]

## Source
- Analysis Report: [path to analysis artifacts]
- Analysis Date: [ISO 8601]
- Scope: [what was analyzed]

## Items for Implementation

### Features/Requirements
| ID | Type | Domain | Description | Dependencies | Priority |
|----|------|--------|-------------|--------------|----------|
| REQ-001 | FEATURE | BACKEND | [Clear, actionable description] | None | P1-High |

### Bug Fixes
| ID | Type | Domain | Description | Dependencies | Priority |
|----|------|--------|-------------|--------------|----------|
| BUG-001 | BUGFIX | FRONTEND | [Issue description] | None | P0-Critical |

### Improvements
| ID | Type | Domain | Description | Dependencies | Priority |
|----|------|--------|-------------|--------------|----------|
| IMP-001 | IMPROVEMENT | BACKEND | [Enhancement description] | REQ-001 | P2-Medium |

### Documentation
| ID | Type | Domain | Description | Dependencies | Priority |
|----|------|--------|-------------|--------------|----------|
| DOC-001 | DOC | DOCS | [Doc task description] | None | P2-Medium |

### Refactoring
| ID | Type | Domain | Description | Dependencies | Priority |
|----|------|--------|-------------|--------------|----------|
| REF-001 | REFACTOR | BACKEND | [Refactor description] | BUG-001 | P3-Low |

## Dependencies
[Inherited from analysis or newly identified]

## Notes
[Any context from analysis that implementation needs]
```

### 6.2 Key Integration Points

| Aspect | Spec-Panel Output | Roadmap Generator Input |
|--------|-------------------|------------------------|
| File format | Markdown | Markdown |
| ID scheme | Pre-assigned or generator-assigned | Uses existing IDs or assigns new |
| Type values | `FEATURE`, `BUGFIX`, `IMPROVEMENT`, `REFACTOR`, `DOC` | Same enum |
| Domain values | From domain enum | From domain enum |
| Dependencies | ID references or `None`/`TBD` | Same format |
| Priority | `P0`-`P3` format | Same enum |

### 6.3 Optional Pre-Processing

If spec-panel items don't have IDs, the roadmap generator will assign them during Phase 1. However, for better traceability, pre-assigning IDs is recommended.

### 6.4 Validation Handoff

Before passing to roadmap generator, spec-panel should ensure:
- [ ] All items have clear, actionable descriptions
- [ ] Type values match the enum (FEATURE, BUGFIX, IMPROVEMENT, REFACTOR, DOC)
- [ ] Domain values match the enum
- [ ] Dependencies reference valid IDs or use `None`/`TBD`
- [ ] Priorities use `P0-Critical`, `P1-High`, `P2-Medium`, or `P3-Low`

---

## 7. Milestone Formation Rules

### 7.1 Ordering Principles

1. **DEPENDENCY-FIRST**: Items with no dependencies scheduled early (Milestone 1)
2. **NATURAL GROUPING**: Cluster related items into cohesive milestones
3. **RISK STRATIFICATION**: High-risk/foundational changes earlier
4. **SIZE LIMITS**: Max 7 deliverables per milestone

### 7.2 Standard Progression Pattern

| Milestone | Typical Content |
|-----------|-----------------|
| M1 | Foundation (setup, infrastructure, dependencies) |
| M2 to M(N-2) | Feature implementation (in dependency order) |
| M(N-1) | Integration and cross-cutting concerns |
| M(N) | Polish, documentation, release prep |

### 7.3 Traceability Requirements

- Every item from `extraction.md` MUST appear in exactly one milestone deliverables table
- Cross-reference integrity: extraction item count MUST equal sum of all milestone deliverables

---

## 8. Persona Selection Algorithm

### 8.1 Selection Rules

| Condition | Action |
|-----------|--------|
| Single domain >40% of items | Primary persona = that domain |
| No dominant domain | Primary persona = ARCHITECTURE |
| Domain >15% of items | Becomes consulting persona |

### 8.2 Domain-to-Persona Mapping

| Domain | Persona |
|--------|---------|
| FRONTEND | Frontend |
| BACKEND | Backend |
| ARCHITECTURE | Architect |
| SECURITY | Security |
| DOCS | Scribe |
| DEVOPS | DevOps |
| TESTING | QA |

---

## 9. File Structure

### 9.1 Output Directory Structure

```
.roadmaps/
  [version]/
    v1/                         # Draft version
      extraction.md
      roadmap.md
      test-strategy.md
      execution-prompt.md
      template-selection.md     # Phase 2.5 output (if applicable)
    v2/                         # Upgraded version (if applicable)
      extraction.md             # Copied from v1
      roadmap.md                # Upgraded
      roadmap.draft.md          # Pre-upgrade copy
      test-strategy.md          # Upgraded
      test-strategy.draft.md
      execution-prompt.md       # Upgraded
      execution-prompt.draft.md
      upgrade-log.md            # Phase 7 results
      consistency-report.md     # Phase 7.5 results
```

---

## 10. Usage Recommendations

### 10.1 Spec-Panel to Roadmap Workflow

```
1. Run spec-panel analysis on requirements/documentation
2. Spec-panel outputs implementation specification with ID scheme
3. Invoke roadmap generator with spec-panel output as input
4. Review extraction.md (Phase 1 gate)
5. Approve roadmap.md (Phase 3 gate)
6. Approve test-strategy.md (Phase 4 gate)
7. Use execution-prompt.md for implementation
```

### 10.2 Command Invocation

```bash
# Basic invocation
/rf:roadmap-gen path/to/spec-panel-output.md

# Draft only (no upgrades)
/rf:roadmap-gen path/to/spec.md --no-upgrade

# With custom output directory
/rf:roadmap-gen path/to/spec.md --output my-release

# Multiple upgrade iterations
/rf:roadmap-gen path/to/spec.md --version 3
```

---

## References

- **Roadmap Generator Prompt**: `<project-root>/.dev/releases/backlog/v.4.1-roadmap-gen/Roadmap-Generator-Prompt.md`
- **v3.0 Specification**: `<project-root>/.dev/releases/backlog/v.4.1-roadmap-gen/v3.0_Roadmap-Generator-Specification.md`
- **Extraction Example**: `<project-root>/.dev/releases/backlog/v.4.1-roadmap-gen/extraction.md`
- **Roadmap Example**: `<project-root>/.dev/releases/backlog/v.4.1-roadmap-gen/roadmap.md`
- **Test Strategy Example**: `<project-root>/.dev/releases/backlog/v.4.1-roadmap-gen/test-strategy.md`
- **Execution Prompt Example**: `<project-root>/.dev/releases/backlog/v.4.1-roadmap-gen/execution-prompt.md`
