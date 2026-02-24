# Templates Reference

Reference document for Wave 2 (Planning & Template Selection) and Wave 3 (Generation). Contains template discovery, milestone planning, effort estimation, body templates for roadmap.md and test-strategy.md, and YAML frontmatter schemas.

---

## 4-Tier Template Discovery

Templates are discovered in priority order. The first tier to produce a match is used; lower tiers are not searched.

### Tier 1: Local (Project-Level)

**Search path**: `.dev/templates/roadmap/` in the current project directory.

**Discovery**: Glob for `*.md` and `*.yaml` files in this directory. Each file must contain YAML frontmatter with at least `name`, `type`, and `domains` fields to be considered a valid template.

### Tier 2: User (User-Level)

**Search path**: `~/.claude/templates/roadmap/`

**Discovery**: Same glob and validation rules as Tier 1.

### Tier 3: Plugin (Marketplace)

**Status**: `[future: v5.0 plugin marketplace — plumb in here when available]`

**Search path**: Will be defined when the plugin marketplace is implemented. Expected pattern: `~/.claude/plugins/*/templates/roadmap/`

**Current behavior**: This tier is always a no-op. Skip to Tier 4.

### Tier 4: Inline Generation (Fallback)

**Trigger**: No template found in Tiers 1-3, OR no template scores >= 0.6 in compatibility scoring, OR `--template` flag specifies a type with no matching file.

**Behavior**: Generate a milestone structure directly from the extraction data using the milestone count selection and domain-specific mapping rules below.

---

## Template File Format

Templates discovered in Tiers 1-3 must follow this format:

```yaml
---
name: <template-name>
type: <feature|quality|docs|security|performance|migration>
domains: [<domain1>, <domain2>]
target_complexity: <0.0-1.0>
min_version: "<semver>"
milestone_count_range: [<min>, <max>]
---
# Template body with milestone structure
```

**Required fields**: `name`, `type`, `domains`
**Optional fields**: `target_complexity` (default 0.5), `min_version` (default "1.0.0"), `milestone_count_range` (default from complexity class)

---

## Version Resolution Rules

When multiple template files match the same `type`:
1. Filter: exclude templates where `min_version` > current sc:roadmap version
2. Score: apply template compatibility scoring (see `refs/scoring.md`)
3. Select: highest-scoring template wins
4. Tie-break: if scores are equal, prefer Tier 1 over Tier 2 (local project customization wins)

---

## Matching Criteria

A template is considered a **candidate** if:
1. Its `type` field matches the spec's dominant requirement type OR the user's `--template` flag value
2. Its `min_version` is <= current sc:roadmap version
3. It has valid YAML frontmatter with required fields

Candidates are then scored using the template compatibility formula from `refs/scoring.md`. Only templates scoring >= 0.6 are selected.

---

## Inline Template Generation Fallback

When no template scores >= 0.6 (or no templates exist), generate the milestone structure algorithmically.

### Milestone Count Selection

| Complexity Class | Milestone Count | Rationale |
|-----------------|----------------|-----------|
| LOW (< 0.4) | 3-4 | Simple scope, few dependencies |
| MEDIUM (0.4-0.7) | 5-7 | Moderate scope, cross-domain work |
| HIGH (> 0.7) | 8-12 | Complex scope, many dependencies |

**Exact count within range**: `base + floor(domain_count / 2)`
- LOW: base = 3
- MEDIUM: base = 5
- HIGH: base = 8
- `domain_count` = number of domains with >= 10% representation

### Domain-Specific Milestone Mapping

Each domain detected with >= 10% representation generates at least one dedicated milestone. The milestone type and focus depends on the domain.

| Domain | Milestone Type | Typical Focus |
|--------|---------------|---------------|
| frontend | FEATURE | UI components, user flows, accessibility |
| backend | FEATURE | API endpoints, data models, service logic |
| security | SECURITY | Authentication, authorization, threat mitigation |
| performance | IMPROVEMENT | Optimization, caching, load testing |
| documentation | DOC | User guides, API docs, architecture docs |

### Milestone Generation Algorithm

1. **Foundation milestone** (always M1): Project setup, dependencies, architecture decisions. Type: FEATURE. Priority: P0.
2. **Domain milestones**: One per domain with >= 10%, ordered by domain percentage (highest first). Type from domain mapping above.
3. **Integration milestone**: If domain_count >= 2, add an integration milestone after domain milestones. Type: TEST. Priority: P1.
4. **Validation milestone**: Final milestone for end-to-end validation and acceptance testing. Type: TEST. Priority: P1.

**Validation milestone interleaving**: Based on interleave ratio from complexity class (see `refs/scoring.md`):
- LOW (1:3): Insert validation milestone after every 3 work milestones
- MEDIUM (1:2): Insert validation milestone after every 2 work milestones
- HIGH (1:1): Insert validation milestone after every work milestone

### Priority Assignment

Milestones are assigned priorities based on dependency depth and domain criticality:

| Priority | Assignment Rule |
|----------|----------------|
| P0 | Foundation milestone (M1); milestones containing security requirements; milestones with no dependencies that other milestones depend on |
| P1 | Domain milestones for dominant domain (highest %); milestones on the critical dependency path |
| P2 | Domain milestones for secondary domains; integration milestones |
| P3 | Documentation milestones; validation milestones (they validate but don't produce features) |

**Tie-breaking**: When multiple rules apply, use the highest priority (P0 > P1 > P2 > P3).

### Dependency Mapping Rules

- M1 (Foundation) has no dependencies
- Domain milestones depend on M1
- Domain milestones for related domains may have inter-dependencies (e.g., backend milestone blocks frontend milestone if frontend requires API endpoints)
- Integration milestones depend on all domain milestones they integrate
- Validation milestones depend on the work milestones they validate
- **Cycle detection**: After mapping, verify no circular dependencies exist. If a cycle is detected, break it by removing the dependency with the weakest relationship (lowest domain overlap between the two milestones).

### Required Sections Per Milestone

Every generated milestone must include these sections (matching the roadmap.md body template):

1. **Objective**: 1-2 sentence goal statement
2. **Deliverables**: Table with ID, description, acceptance criteria
3. **Dependencies**: List of prerequisite milestones or "None"
4. **Risk Assessment**: Table with risk, probability, impact, mitigation

---

## Effort Estimation

Each milestone receives an effort estimate based on its deliverable count, complexity contribution, and risk profile. Effort is expressed as relative levels (not time estimates).

### Effort Levels

| Level | Deliverable Count | Complexity Factor | Typical Scope |
|-------|-------------------|-------------------|---------------|
| XS | 1-2 | < 0.3 | Single-concern, minimal dependencies |
| S | 3-4 | 0.3-0.5 | Focused scope, few dependencies |
| M | 5-7 | 0.5-0.7 | Multi-concern, cross-dependency |
| L | 8-10 | 0.7-0.85 | Broad scope, significant integration |
| XL | 11+ | > 0.85 | System-wide, many dependencies |

### Estimation Algorithm

For each milestone:

1. **Count deliverables**: `deliverable_count` = number of D#.# items in the milestone
2. **Compute complexity contribution**: `complexity_factor` = (milestone's requirements / total requirements) * complexity_score
3. **Assess risk multiplier**:
   - No High risks: multiplier = 1.0
   - 1 High risk: multiplier = 1.2
   - 2+ High risks: multiplier = 1.5
4. **Compute adjusted count**: `adjusted = deliverable_count * risk_multiplier`
5. **Map to effort level** using the table above (use `adjusted` count and `complexity_factor`, whichever maps to the higher effort level)

### Risk Level Assignment

Each milestone's risk level is derived from the risks in extraction.md that map to its requirements:

| Risk Level | Condition |
|------------|-----------|
| Low | No High-probability or High-impact risks associated with milestone requirements |
| Medium | At least 1 Medium-probability AND Medium-impact risk, OR 1 High in either dimension |
| High | At least 1 High-probability AND High-impact risk, OR 2+ High risks in any dimension |

---

## roadmap.md Body Template

This template defines the body structure for the generated roadmap.md (follows the YAML frontmatter). All sections are required.

```markdown
# Roadmap: <Project Title>

## Overview
<1-3 paragraph summary of the roadmap scope, approach, and key decisions made during planning>

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | <title> | FEATURE | P0 | S | None | 3 | Low |
| M2 | <title> | SECURITY | P1 | M | M1 | 5 | Medium |
| ... | | | | | | | |

## Dependency Graph
<Textual representation of milestone dependencies using arrow notation>
<Example: M1 → M2 → M4, M1 → M3 → M4, M5 (independent)>

---

## M1: <Milestone Title>

### Objective
<1-2 sentence clear milestone goal>

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | <deliverable> | <measurable outcome> |
| D1.2 | <deliverable> | <measurable outcome> |

### Dependencies
- None (first milestone) OR
- M{N}: <what is needed from that milestone>

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| <risk> | Low/Medium/High | Low/Medium/High | <mitigation> |

---

## M2: <Milestone Title>
[Same structure as M1]

---
[Repeat for all milestones]

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | <risk> | M1, M3 | Medium | High | <mitigation> | <persona> |
| R-002 | <risk> | M2 | Low | Medium | <mitigation> | <persona> |

## Decision Summary

Records key decisions made during roadmap generation for auditability and downstream context. **Every row must cite the specific data point that drove the decision — no subjective justifications.**

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | <persona> | <other candidates with confidence scores> | <highest domain % or --persona override> |
| Template | <template-name or "inline"> | <other templates with compatibility scores> | <best match score or fallback reason> |
| Milestone Count | <N> | <range considered> | <complexity class → count formula result> |
| Adversarial Mode | <mode or "none"> | N/A | <flags present or absent> |
| Adversarial Base Variant | <model:persona or "N/A"> | <other variants with scores> | <highest convergence contribution> |

## Success Criteria
<Derived from spec success criteria in extraction.md, mapped to milestones>

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | <criterion> | M1, M2 | Yes |
| SC-002 | <criterion> | M3 | Yes |
```

---

## test-strategy.md Body Template

This template defines the body structure for test-strategy.md (follows the YAML frontmatter). Generated AFTER roadmap.md is complete (sequencing constraint). All sections are required.

```markdown
# Test Strategy: Continuous Parallel Validation

## Validation Philosophy

This test strategy implements **continuous parallel validation** — the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is <ratio> (one validation milestone per <N> work milestones), derived from complexity class <class>

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 | M<N> (<title>) | <what is validated> | <specific stop condition> |
| V2 | M<N> (<title>) | <what is validated> | <specific stop condition> |
| ... | | | |

**Placement rule**: Validation milestones are placed after every <N> work milestones per the interleave ratio. Each validation milestone references the specific work milestones it validates by M# ID.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Breaking dependency, security flaw, data loss risk |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Missing core requirement, broken integration point |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Documentation gap, style inconsistency, minor tech debt |
| Info | Log only, no action required | N/A | Optimization opportunity, alternative approach noted |

## Acceptance Gates

Per-milestone acceptance criteria derived from spec requirements and mapped to deliverables.

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M<N> | <specific criteria from deliverable ACs> | All deliverable ACs met, no Critical/Major issues |
| M<N> | <specific criteria> | <specific condition> |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 | V1 | M<N> | <how validated> |
| FR-002 | V2 | M<N> | <how validated> |
| NFR-001 | V<N> | M<N> | <how validated> |
```

---

## YAML Frontmatter Schemas

All 3 output artifacts include YAML frontmatter as a versioned contract for downstream consumption. **Fields may be added but never removed or renamed** (contract stability per NFR-003).

### Mutual Exclusion Rule

**Exactly one** of `spec_source` or `spec_sources` must be present in each artifact's frontmatter:
- **Single-spec mode**: `spec_source: <path>` (scalar string)
- **Multi-spec mode**: `spec_sources: [<path1>, <path2>, ...]` (list)
- Never include both fields. Never omit both fields.

### roadmap.md Frontmatter

```yaml
---
spec_source: <path-to-source-spec>                  # Single-spec mode (scalar)
# OR
spec_sources: [<path1>, <path2>]                     # Multi-spec mode (list)
generated: <ISO-8601 timestamp>                      # e.g., 2026-02-22T14:30:00Z
generator: sc:roadmap
complexity_score: <0.0-1.0>
complexity_class: <LOW|MEDIUM|HIGH>
domain_distribution:
  frontend: <percentage>
  backend: <percentage>
  security: <percentage>
  performance: <percentage>
  documentation: <percentage>
primary_persona: <persona-name>
consulting_personas: [<persona1>, <persona2>]
milestone_count: <N>
milestone_index:
  - id: M1
    title: <title>
    type: <FEATURE|IMPROVEMENT|DOC|TEST|MIGRATION|SECURITY>
    priority: <P0|P1|P2|P3>
    dependencies: []                                 # Empty list for M1
    deliverable_count: <N>
    risk_level: <Low|Medium|High>
  - id: M2
    title: <title>
    type: <type>
    priority: <priority>
    dependencies: [M1]
    deliverable_count: <N>
    risk_level: <level>
total_deliverables: <N>
total_risks: <N>
estimated_phases: <N>                                # Hint for future tasklist generator
validation_score: <0.0-1.0>                          # From Wave 4 (0.0 if --no-validate)
validation_status: <PASS|REVISE|REJECT|PASS_WITH_WARNINGS|SKIPPED>
adversarial:                                         # Present ONLY if adversarial mode used
  mode: <multi-spec|multi-roadmap|combined>
  agents: [<agent-spec-1>, <agent-spec-2>]
  convergence_score: <0.0-1.0>
  base_variant: <model:persona>
  artifacts_dir: <path-to-adversarial-artifacts>
---
```

### extraction.md Frontmatter

```yaml
---
spec_source: <path>                                  # Single-spec mode
# OR
spec_sources: [<path1>, <path2>]                     # Multi-spec mode
generated: <ISO-8601 timestamp>
generator: sc:roadmap
functional_requirements: <count>
nonfunctional_requirements: <count>
total_requirements: <count>                          # FR + NFR
domains_detected: [<domain1>, <domain2>]
complexity_score: <0.0-1.0>
complexity_class: <LOW|MEDIUM|HIGH>
risks_identified: <count>
dependencies_identified: <count>
success_criteria_count: <count>
extraction_mode: <standard|chunked>                  # "chunked (N chunks)" if chunked
---
```

### test-strategy.md Frontmatter

```yaml
---
spec_source: <path>                                  # Single-spec mode
# OR
spec_sources: [<path1>, <path2>]                     # Multi-spec mode
generated: <ISO-8601 timestamp>
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: <count>                       # Number of V# milestones
work_milestones: <count>                             # Number of M# work milestones
interleave_ratio: "<validation>:<work>"              # e.g., "1:2" for MEDIUM complexity
major_issue_policy: stop-and-fix
complexity_class: <LOW|MEDIUM|HIGH>
---
```

---

*Reference document for sc:roadmap v2.0.0 — loaded on-demand during Wave 2, available through Wave 3*
