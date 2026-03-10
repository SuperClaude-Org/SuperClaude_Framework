# D-0005: Release Spec Template

Template file created at: `src/superclaude/examples/release-spec-template.md`

## Section Mapping (1:1 with spec section-to-source mapping table)

| # | Template Section | Spec Source (from FR-060.1 3b mapping table) | Present |
|---|-----------------|----------------------------------------------|---------|
| 1 | Problem Statement | Derive from source workflow's purpose | Yes |
| 2 | Solution Overview (+ 2.2 Workflow) | Phase 2 pipeline architecture / Phase 1 data flow | Yes |
| 3 | Functional Requirements | One FR per step from Phase 2 step_mapping | Yes |
| 4 | Architecture (+ 4.5 Data Models, 4.6 Impl Order) | Phase 2 module_plan / Phase 0 prerequisites | Yes |
| 5 | Interface Contracts (+ 5.2 Gate Criteria, 5.3 Phase Contracts) | Phase 2 gate_definitions / Phase 1+2 contracts | Yes |
| 6 | Non-Functional Requirements | Standard portification NFRs | Yes |
| 7 | Risk Assessment | Phase 1 classification confidence scores | Yes |
| 8 | Test Plan | Phase 2 pattern coverage matrix | Yes |
| 9 | Migration & Rollout | Breaking changes / backwards compatibility | Yes |
| 10 | Downstream Inputs | Themes for sc:roadmap, tasks for sc:tasklist | Yes |
| 11 | Open Items | Unresolved questions with owners | Yes |
| 12 | Brainstorm Gap Analysis | Phase 3c embedded brainstorm output | Yes |

## Frontmatter Schema

Includes quality score fields: `clarity`, `completeness`, `testability`, `consistency`, `overall`

## Sentinel Format

All placeholders use `{{SC_PLACEHOLDER:name}}` format (Constraint 5).
Total sentinel count: 57 intentional placeholders.
