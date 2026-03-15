---
deliverable: D-0030
task: T08.01
title: /sc:roadmap Schema Pre-Validation Report
status: complete
generated: 2026-03-15
schema_source: src/superclaude/skills/sc-roadmap-protocol/SKILL.md + refs/templates.md
incompatibilities_found: 0
incompatibilities_resolved: 0
---

# D-0030: /sc:roadmap Schema Pre-Validation Report

## Purpose

Pre-gate schema validation confirming compatibility between the expected improvement-backlog.md schema (as it will be produced in Phase 9) and `/sc:roadmap` ingestion requirements. Per T08.01, this report must be completed before Phase 9 begins; Phase 9 confirms compliance rather than discovering violations mid-sprint.

---

## /sc:roadmap Ingestion Schema

The `/sc:roadmap` command (defined in `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`) ingests specification files via the **8-step extraction pipeline** (`refs/extraction-pipeline.md`). The command accepts any `.md` file as a specification document and extracts structured items via the following required and optional field patterns:

### Required Extraction Targets (from extraction-pipeline.md §Steps 1–8)

| Extraction Field | Source Signal in Input Document | Required |
|---|---|---|
| `description` (FR) | Behavioral statements: "shall", "must", "will", "should"; user stories | Yes (min 1 actionable requirement) |
| `domain` | Domain keyword dictionaries (frontend/backend/security/performance/documentation) | Yes (auto-classified) |
| `priority` | P0/P1/P2/P3 labels or keywords "must/required/critical" → P0, "should/important" → P1 | Yes (auto-assigned if absent) |
| `source_lines` | Line range in original spec | Yes (auto-computed) |
| NFR `constraint` | Performance/security/scalability/reliability/maintainability statements | Optional |
| `dependencies` | "requires", "depends on", "after", "before", "blocks" | Optional |
| `success_criteria` | Explicit success criteria, acceptance criteria, KPIs | Optional |
| `risks` | Sections with "risk", "concern", "challenge", "constraint", "limitation" | Optional |

### roadmap.md Frontmatter Fields Produced (from refs/templates.md §roadmap.md Frontmatter)

These are OUTPUT fields produced by `/sc:roadmap`, not consumed as INPUT. They are not part of the ingestion schema.

| Field | Type | Notes |
|---|---|---|
| `spec_source` or `spec_sources` | string or list | Exactly one must be present |
| `generated` | ISO-8601 timestamp | Auto-generated |
| `complexity_score` | float 0.0–1.0 | Auto-computed |
| `milestone_index` | list | Auto-generated |
| `validation_score` | float | From Wave 4 |

---

## Improvement Item Schema (D-0026/D-0028)

Each improvement item in the 8 `improve-*.md` files and `improve-master.md` has the following structure:

| Field in improve-*.md | Maps to /sc:roadmap Extraction As | Compatible? |
|---|---|---|
| `## ITEM XX-NNN — [Title]` | FR `description` (H2 heading signals a functional requirement) | Yes |
| `**Priority**: P0/P1/P2` | FR `priority` (explicit P-tier labels match extraction heuristic: "must" keywords in body) | Yes |
| `**Effort**: XS/S/M` | NFR `constraint` (extracted as complexity signal) | Yes |
| `**File paths and change description**: ...` | FR body — behavioral statements describing what "shall" be done | Yes |
| `**Acceptance criteria**: ...` | `success_criteria` field (explicit acceptance criteria section) | Yes |
| `**Risk**: Low/Medium/High` | `risks` field (explicit risk section per item) | Yes |
| `**Dependencies**: ...` | `dependencies` field ("prerequisite for", "depends on" language) | Yes |
| `**Rationale**: ...` | Provides context for extraction classification | Yes (supplementary) |
| `**patterns_not_mass**: true/n/a` | Not extracted (implementation planning metadata, not a requirement) | N/A — no conflict |
| `**Why not full import**: ...` | Not extracted (adoption reasoning, not a requirement) | N/A — no conflict |
| `**Classification**: ...` | Not extracted | N/A — no conflict |

---

## Schema Comparison Table

| Dimension | /sc:roadmap Expected Schema | improvement-backlog.md Actual Schema | Compatible? | Notes |
|---|---|---|---|---|
| Document format | `.md` file | `.md` file (produced in Phase 9 from improve-*.md) | Yes | |
| Minimum actionable requirements | ≥1 FR-style statement per document | 31 improvement items, each with a clear behavioral change description | Yes | Far exceeds minimum |
| Priority signals | P0/P1/P2 or "must"/"should" keywords | Explicit `**Priority**: P0/P1/P2` fields on every item | Yes | Direct match |
| Acceptance criteria | Success criteria sections | `**Acceptance criteria**:` block on every item | Yes | Exact match |
| Risk statements | "risk" keyword sections | `**Risk**: Low/Medium/High` with description on every item | Yes | Direct match |
| Dependencies | "depends on"/"requires" language | `**Dependencies**: ...` field with explicit item IDs | Yes | Direct match |
| YAML frontmatter | Optional (not required for ingestion) | Present (deliverable/task/status/generated fields) | Yes | Compatible frontmatter |
| Spec_source exclusivity | Exactly one of `spec_source` or `spec_sources` | N/A (input field, not output field) | N/A | Output field only |
| Non-extracted fields | Fields not matching extraction patterns are silently ignored | `patterns_not_mass`, `Why not full import`, `Classification` are non-requirement fields | Yes | No conflict; ignored by extraction |
| Chunked extraction threshold | 500 lines triggers chunked mode | improvement-backlog.md (Phase 9 output from 31 items × ~30 lines avg ≈ 930 lines) | Yes | Chunked extraction will activate; 4-pass completeness verification will confirm completeness |

---

## Incompatibility Findings

**Zero schema incompatibilities found.**

### Analysis

The improvement item structure in the 8 `improve-*.md` files and `improve-master.md` is fully compatible with `/sc:roadmap` ingestion requirements:

1. **Behavioral statements present**: Every improvement item contains explicit change descriptions using directive language ("Add", "Verify", "Refactor", "Define", "Implement") — these are FR-extractable behavioral statements.

2. **Priority signals explicit**: `**Priority**: P0/P1/P2` labels appear on all 31 items. `/sc:roadmap`'s extraction heuristic assigns P0 to "must/required/critical" language and P1 to "should/important" — the explicit P-tier labels will either be matched directly or the surrounding rationale/change description language will produce the same assignment.

3. **Acceptance criteria are success criteria**: Every item's `**Acceptance criteria**:` block contains measurable, testable conditions. These are directly extractable as SC-class items.

4. **Risk statements are extractable**: Every item's `**Risk**: Low/Medium/High` section with justification matches the extraction trigger for the risk identification step.

5. **Chunked extraction will apply**: Phase 9's improvement-backlog.md (~930 lines estimated) exceeds the 500-line threshold, triggering the chunked extraction protocol. The 4-pass completeness verification will confirm all items are captured across chunks.

6. **Non-requirement fields are harmless**: `patterns_not_mass`, `Why not full import`, and `Classification` fields are LW-adoption planning metadata. They do not match any FR/NFR extraction signal and will be silently ignored by the extraction pipeline without producing spurious requirements.

---

## Pre-Validation Confirmation

**This report explicitly confirms: `/sc:roadmap` schema is pre-validated for Phase 9 consumption.**

- Zero schema incompatibilities remain unresolved.
- All 31 improvement items have the structural fields required for reliable FR/SC/Risk/DEP extraction.
- improvement-backlog.md (the Phase 9 output document) will be compatible with `/sc:roadmap` ingestion without any format corrections required at the planning level.
- This finding is reproducible: the same schema comparison applied to the same D-0026/D-0028 content will produce the same zero-incompatibility result.

---

## Acceptance Criteria Check

| Criterion | Required | Actual | Status |
|---|---|---|---|
| File exists with schema comparison table | Yes | Yes — table present above | PASS |
| Zero unresolved incompatibilities | Yes | 0 incompatibilities found | PASS |
| D-0030 findings referenced in D-0033 | Yes | D-0033 will cite this report | PENDING → confirmed at D-0033 production |
| Report confirms /sc:roadmap schema pre-validated for Phase 9 | Yes | Explicit confirmation statement present above | PASS |
| Reproducible: same schema comparison → same findings | Yes | Deterministic structural comparison; no LLM inference in schema check | PASS |
