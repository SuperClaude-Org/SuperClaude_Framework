# D-0024 — Spec: Artifact Gate Specification and Standards

**Task**: T04.03
**Date**: 2026-02-24
**Status**: COMPLETE
**Tier**: STRICT

## Purpose

Defines quality gates for the 3 sc:roadmap output artifacts: `roadmap.md`, `extraction.md`, and `test-strategy.md`. Each gate specifies required sections, structural validation rules, and minimum content criteria. Gates are deterministic: same input → same pass/fail result.

## Gate Specification Format

Each gate consists of:
1. **Frontmatter Gate**: Required YAML frontmatter fields with type constraints
2. **Body Gate**: Required markdown sections with minimum content criteria
3. **Structural Gate**: Cross-field consistency checks and relationships

---

## Gate 1: roadmap.md

### Frontmatter Gate

| Field | Type | Required | Constraint |
|-------|------|----------|------------|
| `spec_source` XOR `spec_sources` | scalar XOR list | Yes (exactly one) | Mutual exclusion: never both, never neither |
| `generated` | string (ISO-8601) | Yes | Must be valid ISO-8601 timestamp |
| `generator` | string | Yes | Must equal `sc:roadmap` |
| `complexity_score` | float | Yes | Range: 0.0–1.0 |
| `complexity_class` | enum | Yes | One of: LOW, MEDIUM, HIGH |
| `domain_distribution` | object | Yes | Must contain 5 keys: frontend, backend, security, performance, documentation |
| `primary_persona` | string | Yes | Non-empty |
| `consulting_personas` | list | Yes | May be empty list |
| `milestone_count` | integer | Yes | Range: 3–15 |
| `milestone_index` | list[object] | Yes | Length must equal `milestone_count` |
| `total_deliverables` | integer | Yes | >= 1 |
| `total_risks` | integer | Yes | >= 0 |
| `estimated_phases` | integer | Yes | >= 1 |
| `validation_score` | float | Yes | Range: 0.0–1.0 |
| `validation_status` | enum | Yes | One of: PASS, REVISE, REJECT, PASS_WITH_WARNINGS, SKIPPED |
| `adversarial` | object | Conditional | Required only when adversarial mode used; absent otherwise |

**milestone_index entry fields** (per milestone):
| Field | Type | Required |
|-------|------|----------|
| `id` | string | Yes (format: M\d+) |
| `title` | string | Yes (non-empty) |
| `type` | enum | Yes (FEATURE\|IMPROVEMENT\|DOC\|TEST\|MIGRATION\|SECURITY) |
| `priority` | enum | Yes (P0\|P1\|P2\|P3) |
| `dependencies` | list | Yes (may be empty) |
| `deliverable_count` | integer | Yes (>= 1) |
| `risk_level` | enum | Yes (Low\|Medium\|High) |

**adversarial block fields** (when present):
| Field | Type | Required |
|-------|------|----------|
| `mode` | enum | Yes (multi-spec\|multi-roadmap\|combined) |
| `agents` | list[string] | Yes (length 2-10) |
| `convergence_score` | float | Yes (0.0-1.0) |
| `base_variant` | string | Conditional (required in multi-roadmap/combined) |
| `artifacts_dir` | string | Yes (non-empty path) |

### Body Gate

| Section | Required | Minimum Content |
|---------|----------|-----------------|
| `# Roadmap: <title>` | Yes | Title non-empty |
| `## Overview` | Yes | >= 1 paragraph (>= 50 characters) |
| `## Milestone Summary` | Yes | Table with >= 3 rows (matching milestone_count) |
| `## Dependency Graph` | Yes | >= 1 line of arrow notation |
| `## M{N}: <title>` | Yes (per milestone) | One section per milestone_count |
| `### Objective` | Yes (per milestone) | >= 1 sentence |
| `### Deliverables` | Yes (per milestone) | Table with >= 1 row |
| `### Dependencies` | Yes (per milestone) | >= 1 bullet or "None" |
| `### Risk Assessment` | Yes (per milestone) | Table with >= 1 row |
| `## Risk Register` | Yes | Table with >= 0 rows |
| `## Decision Summary` | Yes | Table with >= 4 rows (Persona, Template, Milestone Count, Adversarial Mode) |
| `## Success Criteria` | Yes | Table with >= 1 row |

### Structural Gate

| Check | Rule |
|-------|------|
| Milestone count consistency | `milestone_count` in frontmatter == count of `## M{N}` sections == length of `milestone_index` == row count in Milestone Summary table |
| Dependency DAG | All milestone dependencies reference existing milestone IDs; no circular dependencies |
| Domain distribution sum | Sum of `domain_distribution` percentages == 100% (±1% for rounding) |
| Complexity class alignment | `complexity_score` < 0.4 → LOW, 0.4–0.7 → MEDIUM, > 0.7 → HIGH |

---

## Gate 2: extraction.md

### Frontmatter Gate

| Field | Type | Required | Constraint |
|-------|------|----------|------------|
| `spec_source` XOR `spec_sources` | scalar XOR list | Yes (exactly one) | Mutual exclusion |
| `generated` | string (ISO-8601) | Yes | Valid ISO-8601 |
| `generator` | string | Yes | Must equal `sc:roadmap` |
| `functional_requirements` | integer | Yes | >= 0 |
| `nonfunctional_requirements` | integer | Yes | >= 0 |
| `total_requirements` | integer | Yes | Must equal functional_requirements + nonfunctional_requirements |
| `domains_detected` | list[string] | Yes | >= 1 domain |
| `complexity_score` | float | Yes | Range: 0.0–1.0 |
| `complexity_class` | enum | Yes | One of: LOW, MEDIUM, HIGH |
| `risks_identified` | integer | Yes | >= 0 |
| `dependencies_identified` | integer | Yes | >= 0 |
| `success_criteria_count` | integer | Yes | >= 0 |
| `extraction_mode` | string | Yes | "standard" or pattern "chunked (N chunks)" |

### Body Gate

extraction.md body structure is defined by Wave 1B extraction output. Minimum required sections:

| Section | Required | Minimum Content |
|---------|----------|-----------------|
| Requirements listing | Yes | >= 1 requirement with ID |
| Domain analysis | Yes | >= 1 domain identified |
| Complexity assessment | Yes | Score and class present |
| Risks section | Yes | Present (may be empty) |
| Dependencies section | Yes | Present (may be empty) |
| Success criteria | Yes | >= 1 criterion if `success_criteria_count` > 0 |

### Structural Gate

| Check | Rule |
|-------|------|
| Requirement count consistency | `total_requirements` == `functional_requirements` + `nonfunctional_requirements` |
| Domain consistency | `domains_detected` list entries match domains analyzed in body |
| Complexity consistency | `complexity_score` and `complexity_class` match (same thresholds as roadmap.md) |
| Success criteria count | Number of listed criteria == `success_criteria_count` |

---

## Gate 3: test-strategy.md

### Frontmatter Gate

| Field | Type | Required | Constraint |
|-------|------|----------|------------|
| `spec_source` XOR `spec_sources` | scalar XOR list | Yes (exactly one) | Mutual exclusion |
| `generated` | string (ISO-8601) | Yes | Valid ISO-8601 |
| `generator` | string | Yes | Must equal `sc:roadmap` |
| `validation_philosophy` | string | Yes | Must equal `continuous-parallel` |
| `validation_milestones` | integer | Yes | >= 1 |
| `work_milestones` | integer | Yes | >= 3 |
| `interleave_ratio` | string | Yes | Format: "\d+:\d+" (e.g., "1:2") |
| `major_issue_policy` | string | Yes | Must equal `stop-and-fix` |
| `complexity_class` | enum | Yes | One of: LOW, MEDIUM, HIGH |

### Body Gate

| Section | Required | Minimum Content |
|---------|----------|-----------------|
| `# Test Strategy: Continuous Parallel Validation` | Yes | Exact title |
| `## Validation Philosophy` | Yes | >= 1 paragraph with 5 core principles |
| `## Validation Milestones` | Yes | Table with >= 1 row (matching `validation_milestones`) |
| `## Issue Classification` | Yes | Table with 4 severity levels: Critical, Major, Minor, Info |
| `## Acceptance Gates` | Yes | Table with >= 1 row |
| `## Validation Coverage Matrix` | Yes | Table with >= 1 row |

### Structural Gate

| Check | Rule |
|-------|------|
| Interleave ratio alignment | Complexity class determines ratio: LOW → 1:3, MEDIUM → 1:2, HIGH → 1:1 |
| Milestone reference validity | All V# milestones reference existing M# work milestones |
| Work milestone count | `work_milestones` matches roadmap.md `milestone_count` |
| Validation milestone count | Count of V# entries in table == `validation_milestones` |
| Severity completeness | All 4 severity levels (Critical, Major, Minor, Info) defined |

---

## Gate Pass/Fail Criteria

A gate **PASSES** when:
1. All required frontmatter fields present with correct types
2. All required body sections present with minimum content met
3. All structural consistency checks pass

A gate **FAILS** when:
1. Any required frontmatter field is missing or has wrong type → **ERROR**
2. Any required body section is missing → **ERROR**
3. Any structural check fails → **ERROR**
4. Body section present but below minimum content → **WARNING** (does not fail gate)

## Relationship to Return Contract Schema

The artifact gates reference the return contract schema (D-0010) for consistency:
- `roadmap.md` `adversarial.convergence_score` must match the return contract `convergence_score`
- `roadmap.md` `adversarial.base_variant` must match the return contract `base_variant`
- `roadmap.md` `adversarial.artifacts_dir` must match the return contract `artifacts_dir`

---

*Artifact produced by T04.03*
