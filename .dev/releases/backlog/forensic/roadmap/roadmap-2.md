---
feature: /sc:forensic + sc:forensic-protocol
spec_source: .dev/releases/backlog/forensic/forensic-spec.md
verdicts_source: .dev/releases/backlog/forensic/adversarial/proposal-verdicts.md
roadmap_version: 2.0.0
date: 2026-02-28
template: feature
depth: deep
compliance: strict
status: planning
complexity_score: 0.87
complexity_class: HIGH
primary_persona: architect
supporting_personas: [analyzer, qa, security]
proposals_integrated: 21
proposals_breakdown: "14 ACCEPT + 7 MODIFY (P-022 REJECTED)"
total_milestones: 7
deliverable_count: 2
deliverables:
  - path: .claude/commands/sc/forensic.md
    mirror: src/superclaude/commands/forensic.md
  - path: src/superclaude/skills/sc-forensic-protocol/SKILL.md
estimated_effort: XL
estimated_calendar_weeks: 10-13
validation_status: PASS
validation_score: 0.91
adversarial_status: integrated
collision_suffix: "-2"
---

# /sc:forensic — Implementation Roadmap v2

## Overview

This roadmap governs the implementation of the `/sc:forensic` command and the `sc:forensic-protocol`
skill for the SuperClaude Framework v4.2.0+. It is the definitive planning artifact, generated at
`--depth deep` with `--compliance strict`, incorporating all 21 accepted and modified proposals from
the adversarial debate pipeline (`proposal-verdicts.md`, convergence 1.00).

**Feature summary**: A generic forensic QA and debug pipeline that auto-discovers investigation
domains, runs parallel root-cause analysis with model tiering, delegates hypothesis and fix
validation to the existing `/sc:adversarial` command, delegates implementation to specialist agents,
produces a comprehensive evidence-backed report, and supports checkpoint/resume for long-running
sessions.

**Key design decisions baked into this roadmap**:
- The spec MUST be amended per all 21 validated proposals before any authoring begins (M0-M1)
- All 9 data schemas are finalized in M2 before phase logic is authored (M3+)
- The skill package follows the established pattern: `SKILL.md` + `refs/` subdirectory
- `make sync-dev` + `make verify-sync` are mandatory post-authoring gates (M6)
- Testing covers each pipeline phase independently plus end-to-end (M6)

**Dependency on existing infrastructure** (pre-existing, NOT built by this roadmap):
- `sc:adversarial-protocol` — invoked in Phases 2 and 3b
- `sc:cleanup-audit-protocol` — checkpoint/batch pattern source (read-only reference)
- `sc:task-unified-protocol` — compliance tiering pattern source (read-only reference)

---

## Milestone Summary

| ID | Name | Effort | Depends On | Blocks | Proposals |
|----|------|--------|------------|--------|-----------|
| M0 | Spec Finalization: Critical Blockers (Tier 1) | M | — | M1+ | P-001, P-004, P-005, P-002, P-013 |
| M1 | Spec Finalization: Schema and Behavioral Fixes (Tiers 2-3) | M | M0 | M2+ | P-006–P-012, P-014–P-016 |
| M2 | Foundation: Command Shell, Skill Shell, Finalized Schemas | L | M1 | M3+ | P-008, P-009, P-021 (applied) |
| M3 | Phase 0: Reconnaissance Agents + Domain Discovery | M | M2 | M4 | P-007, P-015 (applied) |
| M4 | Phase 1 + Phase 3: Investigation and Fix Proposal Agents | L | M3 | M5 | P-012, P-016, P-010 (applied) |
| M5 | Phases 2 + 3b: Adversarial Integration + Phase 4-6 Pipeline | L | M4 | M6 | P-003, P-011, P-014, P-017–P-021 (applied) |
| M6 | Testing, Sync, Verification, and Documentation | L | M5 | release | P-015, P-018, P-019, P-020 (validated) |

**Effort key**: XS (<1d) | S (1-2d) | M (3-5d) | L (6-10d) | XL (>10d)

---

## Dependency Graph

```
M0 (Tier 1 spec amendments)
 └── M1 (Tier 2-3 spec amendments)
      └── M2 (Command + Skill shell + finalized schemas)
           ├── M3 (Phase 0: Recon + Domain discovery)
           │    └── M4 (Phase 1 + Phase 3 agents)
           │         └── M5 (Phases 2+3b adversarial + Phases 4-6 pipeline)
           │              └── M6 (Testing + sync + verification)
           └── [schema registry published — all downstream milestones read-only]
```

**Critical path**: M0 → M1 → M2 → M3 → M4 → M5 → M6 (all sequential, no parallelism — spec
correctness is a prerequisite for each authoring stage).

**Parallelism opportunity within M4**: Phase 1 agent logic and Phase 3 agent logic share no
dependencies within the same milestone and can be authored by different contributors simultaneously
once M3 is complete. Similarly, Phases 4 and 5 within M5 can proceed in parallel.

---

## M0: Spec Finalization — Critical Blockers (Tier 1)

**Objective**: Apply the 5 Tier 1 proposals from the adversarial debate verdict as amendments to
the canonical spec (`forensic-spec.md`). These fix structural issues that would cause all
implementations to diverge if not resolved before authoring.

**Why this is M0**: Every subsequent milestone reads the spec. An ambiguous or inconsistent spec
is more expensive to fix mid-implementation than pre-implementation. Estimated rework cost if
deferred: 3-5x the cost of doing it now.

**Deliverables**:

| ID | Deliverable | Proposal | Description |
|----|-------------|---------|-------------|
| D0.1 | Normative requirement markers in spec | P-001 | Add MUST/SHOULD/MAY markers to all 55 FRs and 10 NFRs. Distinguish normative from explanatory text. |
| D0.2 | Standardized output path table | P-004 | Create a single authoritative path table in a new spec Section 12.0 listing every artifact with its canonical relative path. Remove/replace all inline path mentions. |
| D0.3 | Phase 3b output contract clause | P-005 | Add explicit FR specifying `fix-selection.md` schema (ranked fix set with confidence/risk/impact matrix) as Phase 3b's binding output contract consumed by Phase 4. |
| D0.4 | `--depth` precedence rule | P-002 | Add normative clause: when `--depth` is explicitly set, it overrides any inferred depth from `--mode`. Document precedence table. |
| D0.5 | Model-tier fallback specification | P-013 | Add FR: when configured model tier is unavailable, pipeline MUST fall back to the next available tier (Haiku→Sonnet→Opus). Fallback is logged in `progress.json`. |

**Tasks**:

| ID | Task | Complexity | Proposal | Output |
|----|------|------------|---------|--------|
| T0.1 | Audit all 55 FRs and 10 NFRs; add MUST/SHOULD/MAY | S | P-001 | Annotated requirements table |
| T0.2 | Audit all inline path references; build canonical path table | S | P-004 | Section 12.0 in spec |
| T0.3 | Draft `fix-selection.md` schema; add FR-024a | XS | P-005 | New FR in Section 3.1 |
| T0.4 | Write `--depth` precedence rule; add to Section 5.3 | XS | P-002 | Updated flag definitions |
| T0.5 | Write model-tier fallback FR; add to Section 3.1 (Command-Level) | XS | P-013 | New FR in spec |
| T0.6 | Peer review all amendments for internal consistency | S | all | Reviewed spec draft |

**Success Criteria**:

| ID | Criterion | Verification |
|----|-----------|-------------|
| SC-001 | All 55 FRs contain a normative marker (MUST/SHOULD/MAY) | grep/count on spec |
| SC-002 | Section 12.0 path table matches all inline path references | diff audit |
| SC-003 | `fix-selection.md` schema is referenced by Phase 4's input contract | cross-reference check |
| SC-004 | `--depth` flag definition includes explicit precedence statement | spec review |
| SC-005 | Model fallback path is documented and includes `progress.json` logging | spec review |

**Estimated effort**: M (3-5 days)
**Depends on**: nothing
**Blocks**: all subsequent milestones

---

## M1: Spec Finalization — Schema and Behavioral Fixes (Tiers 2-3)

**Objective**: Apply the remaining 16 Tier 2 and Tier 3 proposals as spec amendments. These
complete the data contracts (Tier 2) and define behavioral specifications for edge cases (Tier 3).

**Deliverables**:

| ID | Deliverable | Proposals | Description |
|----|-------------|---------|-------------|
| D1.1 | `new-tests-manifest.json` schema with `schema_version` | P-006 | Full schema including `schema_version` field (QE enhancement). Added to Section 9. |
| D1.2 | Updated `risk-surface.json` schema with `overall_risk_score` + `secrets_exposure` | P-007 | Add `overall_risk_score` (mandatory, range [0.0,1.0], recommended default: max of category scores), `secrets_exposure` category. Agent must document scoring rationale in artifact. |
| D1.3 | Fix tier enforcement constraint in Fix Proposal Schema | P-010 | Add constraint: `fix_options` array MUST contain exactly 3 entries (minimal, moderate, robust). No sparse tiers. Add validation note. |
| D1.4 | Strengthened `progress.json` schema | P-008 | Add REQUIRED fields: `run_id` (UUID), `spec_version`, `phase_status_map` (map of phase→status), `target_paths`. `git_head` REQUIRED when target is a git repo (auto-detected), OPTIONAL otherwise. `flags` RECOMMENDED with warning when absent. |
| D1.5 | Stable domain ID specification | P-009 | Replace numeric domain index with deterministic slug-based `domain_id` (e.g., `dom-subprocess-lifecycle`). Hypothesis IDs use slug: `H-{domain_slug}-{seq}`. Retain numeric display index separately. Update all ID references throughout spec. |
| D1.6 | Multi-root path provenance at domain level | P-021 | Add `target_root` field at domain level in `investigation-domains.json`. File paths within domain are relative to domain's `target_root`. Add domain-split constraint: if a domain spans files from multiple target roots, split into sub-domains. |
| D1.7 | MCP tool contract clause | P-014 | Add FR: pipeline MUST verify MCP server availability (Serena, Sequential, Context7) before Phase 0. If a required server is unavailable, emit warning and activate fallback (per MCP.md circuit breaker table). |
| D1.8 | Tiny target handling rule | P-015 | Add FR: if target paths contain fewer than 5 files, skip domain auto-discovery; treat entire target as a single domain. Include smoke test note: test suite MUST include a 3-5 file smoke test. |
| D1.9 | Three-level token budget policy | P-012 | For each phase, define: (1) soft target (design goal), (2) hard ceiling (~2x soft target, testable), (3) overflow action (summarize/sample/defer with explicit warning artifact). Replace existing token cap statements. |
| D1.10 | Orchestrator fallback behavior | P-011 | Add FR: if any phase agent fails, orchestrator MUST log failure to `progress.json.phase_status_map`, mark phase as `partial`, and offer to continue with available data or abort. |
| D1.11 | `--dry-run` phase plan output | P-003 | Add FR: `--dry-run` flag MUST produce a console-rendered phase plan showing discovered domains, estimated agent count, and estimated model tier before any agents are spawned. |
| D1.12 | Zero-hypothesis handling | P-016 | Add FR: if Phase 2 produces zero hypotheses meeting the confidence threshold, pipeline MUST emit a structured empty-result artifact and halt gracefully rather than proceeding to Phase 3. |

**Tasks**:

| ID | Task | Complexity | Proposals | Output |
|----|------|------------|---------|--------|
| T1.1 | Author `new-tests-manifest.json` schema with `schema_version` | XS | P-006 | Schema in Section 9 |
| T1.2 | Update `risk-surface.json` schema: add `overall_risk_score`, `secrets_exposure` | S | P-007 | Updated schema |
| T1.3 | Add fix tier enforcement constraint to Fix Proposal Schema | XS | P-010 | Schema constraint |
| T1.4 | Author strengthened `progress.json` schema with new required fields | S | P-008 | Updated schema in Section 9.8 |
| T1.5 | Spec-wide slug-based domain ID migration | M | P-009 | Updated IDs throughout spec |
| T1.6 | Add `target_root` to domain schema; add domain-split constraint | S | P-021 | Updated Section 9.4 |
| T1.7 | Write MCP availability check FR | XS | P-014 | New FR |
| T1.8 | Write tiny target handling FR | XS | P-015 | New FR |
| T1.9 | Rewrite all per-phase token budget statements as three-level | M | P-012 | Updated Sections 7.0-7.7 |
| T1.10 | Write orchestrator fallback FR | XS | P-011 | New FR |
| T1.11 | Write `--dry-run` phase plan output FR | XS | P-003 | Updated FR-044 |
| T1.12 | Write zero-hypothesis handling FR | XS | P-016 | New FR |
| T1.13 | Full spec consistency pass after all amendments | M | all | Final amended spec |
| T1.14 | Update Table of Contents and cross-references | S | all | Updated spec |

**Success Criteria**:

| ID | Criterion | Verification |
|----|-----------|-------------|
| SC-006 | `new-tests-manifest.json` schema includes `schema_version` field | schema review |
| SC-007 | `risk-surface.json` schema includes `overall_risk_score` and `secrets_exposure` | schema review |
| SC-008 | Fix Proposal Schema constrains `fix_options` to exactly 3 tiers | schema review |
| SC-009 | `progress.json` schema includes `run_id`, `spec_version`, `phase_status_map`, `target_paths` | schema review |
| SC-010 | All hypothesis IDs use slug format `H-{domain_slug}-{seq}` | grep on spec |
| SC-011 | Each domain in `investigation-domains.json` schema has `target_root` field | schema review |
| SC-012 | MCP availability check FR present and references MCP.md circuit breaker table | cross-ref check |
| SC-013 | Tiny target FR present; smoke test note included | spec review |
| SC-014 | Each phase section contains soft-target, hard-ceiling, overflow-action | count check |
| SC-015 | Orchestrator fallback FR references `progress.json.phase_status_map` | cross-ref check |
| SC-016 | `--dry-run` FR specifies phase plan console output before agent spawn | spec review |
| SC-017 | Zero-hypothesis FR specifies empty-result artifact and graceful halt | spec review |

**Estimated effort**: M (3-5 days)
**Depends on**: M0
**Blocks**: M2+

---

## M2: Foundation — Command Shell, Skill Shell, Finalized Schemas

**Objective**: Author the command file and skill package skeleton — the structural containers that
all subsequent milestones fill in. Establish the finalized schema registry referenced by all
phase logic.

**Key principle**: Author the containers first, fill them in later. This ensures all subsequent
tasks have a consistent place to contribute to and allows parallel authoring within later
milestones.

**Deliverables**:

| ID | Deliverable | Path | Description |
|----|-------------|------|-------------|
| D2.1 | Command file (primary location) | `src/superclaude/commands/forensic.md` | Full command definition: YAML frontmatter, usage, all 10 flags with validated defaults, examples, activation block, boundaries, related commands. |
| D2.2 | Command file (installed location) | `.claude/commands/sc/forensic.md` | Identical content to D2.1 (sync via `make sync-dev`). |
| D2.3 | Skill package directory | `src/superclaude/skills/sc-forensic-protocol/` | Directory created with all subdirectory structure. |
| D2.4 | Skill SKILL.md shell | `src/superclaude/skills/sc-forensic-protocol/SKILL.md` | Full skill metadata, purpose, dependency list, phase architecture overview, MCP routing table, model tier matrix, all ref placeholders. Phase behavior sections are stubs. |
| D2.5 | Refs directory | `src/superclaude/skills/sc-forensic-protocol/refs/` | Directory created. |
| D2.6 | Schema registry ref | `src/superclaude/skills/sc-forensic-protocol/refs/schemas.md` | All 9 finalized schemas in authoritative YAML form (incorporating M0-M1 amendments): structural-inventory, dependency-graph, risk-surface, investigation-domains, hypothesis-finding, fix-proposal, changes-manifest, new-tests-manifest, progress. |
| D2.7 | MCP routing ref | `src/superclaude/skills/sc-forensic-protocol/refs/mcp-routing.md` | Per-phase MCP server assignment, tool names, fallback behavior per MCP.md circuit breaker table. |

**Tasks**:

| ID | Task | Complexity | Output |
|----|------|------------|--------|
| T2.1 | Author command YAML frontmatter (flags, tools, personas, mcp-servers) | S | forensic.md frontmatter |
| T2.2 | Author all 10 flag definitions with types, defaults, constraints (from amended spec §5.3) | S | Flag table in forensic.md |
| T2.3 | Author usage examples section (6 examples from spec §5.4) | XS | Examples section |
| T2.4 | Author activation block (`Skill sc:forensic-protocol` invocation) | XS | Activation section |
| T2.5 | Author boundaries section (will/will not) | XS | Boundaries section |
| T2.6 | Author related commands table | XS | Related commands section |
| T2.7 | Create skill directory structure | XS | Directory tree |
| T2.8 | Author SKILL.md metadata and dependency declarations | S | SKILL.md header |
| T2.9 | Author phase architecture overview (data flow diagram) in SKILL.md | S | Architecture section |
| T2.10 | Author all 9 finalized schemas in `refs/schemas.md` | L | schemas.md |
| T2.11 | Author MCP routing table in `refs/mcp-routing.md` | S | mcp-routing.md |
| T2.12 | Author model tier decision matrix in SKILL.md | S | Model tier table |
| T2.13 | Stub all 7 phase behavior sections in SKILL.md (Phase 0-6) | S | Phase stubs |
| T2.14 | Run `make sync-dev` and `make verify-sync` | XS | Sync verification |

**Success Criteria**:

| ID | Criterion | Verification |
|----|-----------|-------------|
| SC-018 | `forensic.md` exists at both `src/superclaude/commands/` and `.claude/commands/sc/` | file existence check |
| SC-019 | Command file contains all 10 flags from spec §5.3 with correct defaults | diff against spec |
| SC-020 | Activation block invokes `Skill sc:forensic-protocol` | grep on command file |
| SC-021 | `SKILL.md` exists in `src/superclaude/skills/sc-forensic-protocol/` | file existence check |
| SC-022 | `refs/schemas.md` contains all 9 schemas with P-006–P-009, P-021 amendments applied | schema count + review |
| SC-023 | `refs/mcp-routing.md` matches spec §11 MCP Routing Table | cross-ref |
| SC-024 | `make verify-sync` exits 0 | CI check |

**Estimated effort**: L (6-10 days)
**Depends on**: M1 (amended spec required for accurate schemas and flags)
**Blocks**: M3, M4, M5

---

## M3: Phase 0 — Reconnaissance Agents and Domain Discovery

**Objective**: Author the complete Phase 0 behavior in `SKILL.md` and its supporting refs. This
covers the 3 parallel Haiku recon agents (structural inventory, dependency graph, risk surface)
and the orchestrator's domain generation step. Incorporates P-007 (risk surface amendments),
P-015 (tiny target handling), and P-021 (target_root at domain level).

**Deliverables**:

| ID | Deliverable | Path | Description |
|----|-------------|------|-------------|
| D3.1 | Phase 0 behavior spec in SKILL.md | SKILL.md §Phase 0 | Full behavioral specification: agent prompts for A-0a/0b/0c, orchestrator domain generation prompt, MCP routing, token budget (3-level per P-012), checkpoint update instructions. |
| D3.2 | Phase 0 agent prompt templates ref | `refs/phase0-agents.md` | Standalone, copy-passable prompt templates for A-0a (structural inventory), A-0b (dependency graph), A-0c (risk surface). Includes P-007 amendment: `overall_risk_score` rationale requirement, `secrets_exposure` category. |
| D3.3 | Domain generation prompt | `refs/phase0-agents.md` | Orchestrator domain generation prompt incorporating slug-based IDs (P-009), `target_root` field (P-021), and tiny target bypass rule (P-015). |

**Tasks**:

| ID | Task | Complexity | Proposals | Output |
|----|------|------------|---------|--------|
| T3.1 | Author Agent 0a structural inventory prompt template | S | P-009, P-021 | A-0a prompt |
| T3.2 | Author Agent 0b dependency graph prompt template | S | P-009 | A-0b prompt |
| T3.3 | Author Agent 0c risk surface scan prompt template | M | P-007 | A-0c prompt: include `overall_risk_score` instruction, `secrets_exposure` category, scoring rationale requirement |
| T3.4 | Author orchestrator domain generation prompt | M | P-009, P-015, P-021 | Domain gen prompt: slug IDs, `target_root`, tiny-target bypass (<5 files → single domain) |
| T3.5 | Author Phase 0 three-level token budget section | S | P-012 | Soft: 500 tokens; Hard ceiling: 1,000 tokens; Overflow: emit warning artifact |
| T3.6 | Author Phase 0 MCP routing instructions (Serena `get_symbols_overview`, Context7) | S | P-014 | MCP section in Phase 0 |
| T3.7 | Author Phase 0 checkpoint update instructions | S | P-008 | Checkpoint section |
| T3.8 | Author Phase 0 MCP availability pre-check | S | P-014 | Pre-check block |
| T3.9 | Author `--focus` hint integration into domain generation | S | (FR-040) | Focus hint handling |
| T3.10 | Integrate `--dry-run` phase plan output for Phase 0 | S | P-003 | Dry-run output block |

**Success Criteria**:

| ID | Criterion | Verification |
|----|-----------|-------------|
| SC-025 | Phase 0 section in SKILL.md covers all 3 agent roles plus orchestrator | content review |
| SC-026 | Agent 0c prompt includes `secrets_exposure` category and `overall_risk_score` rationale | content review |
| SC-027 | Domain generation prompt produces slug IDs (kebab-case) | prompt review |
| SC-028 | Tiny target rule (<5 files → single domain) present in domain generation | content review |
| SC-029 | Phase 0 token budget has 3 levels (soft/ceiling/overflow) | count check |
| SC-030 | `target_root` field included in domain generation output | schema cross-ref |
| SC-031 | MCP pre-check block present before Phase 0 execution | content review |

**Estimated effort**: M (3-5 days)
**Depends on**: M2 (SKILL.md shell and schemas.md must exist)
**Blocks**: M4

---

## M4: Phases 1 and 3 — Investigation and Fix Proposal Agents

**Objective**: Author Phase 1 (parallel domain investigation, N agents) and Phase 3 (parallel fix
proposal generation, M agents) in `SKILL.md` and supporting refs. These are the two primary
fan-out phases. Incorporates P-010 (fix tier enforcement), P-012 (three-level budgets), P-016
(zero-hypothesis handling), and P-009 (slug IDs).

**Deliverables**:

| ID | Deliverable | Path | Description |
|----|-------------|------|-------------|
| D4.1 | Phase 1 behavior spec in SKILL.md | SKILL.md §Phase 1 | Parallel agent orchestration, model tier selection logic (risk_score threshold 0.7), investigation agent prompt, Serena/Sequential/Context7 routing, hypothesis ID format using slugs, token budget (3-level). |
| D4.2 | Phase 1 agent prompt template ref | `refs/phase1-agents.md` | Standalone investigation agent prompt template with all required output fields, slug-based hypothesis ID instructions, evidence format requirements, falsification criterion guidance. |
| D4.3 | Phase 3 behavior spec in SKILL.md | SKILL.md §Phase 3 | Parallel agent orchestration per surviving hypothesis cluster, fix proposal agent prompt, fix tier enforcement (exactly 3 tiers), Serena/Context7 routing. |
| D4.4 | Phase 3 agent prompt template ref | `refs/phase3-agents.md` | Fix proposal agent prompt template with all 3 fix tiers enforced, `test_requirements` structure, `diff_preview` format guidance. |
| D4.5 | Zero-hypothesis handling block | SKILL.md §Phase 1 | Behavior when Phase 2 produces zero surviving hypotheses: emit structured empty-result artifact, log to `progress.json`, halt gracefully with user message. |

**Tasks**:

| ID | Task | Complexity | Proposals | Output |
|----|------|------------|---------|--------|
| T4.1 | Author Phase 1 fan-out orchestration logic | M | P-009, P-012 | Phase 1 orchestration section |
| T4.2 | Author model tier selection logic (risk_score >= 0.7 → Sonnet) | S | (FR-010) | Model tier selection block |
| T4.3 | Author investigation agent prompt template | M | P-009 | Phase 1 agent prompt |
| T4.4 | Author Phase 1 three-level token budget | S | P-012 | Soft: 1,000 tokens; Hard: 2,000; Overflow: summarize hypotheses |
| T4.5 | Author Phase 1 MCP routing (Serena find_referencing_symbols, Sequential, Context7) | S | P-014 | Phase 1 MCP section |
| T4.6 | Author Phase 1 checkpoint update instructions | XS | P-008 | Checkpoint section |
| T4.7 | Author zero-hypothesis handling after Phase 2 | S | P-016 | Zero-hypothesis block |
| T4.8 | Author Phase 3 fan-out orchestration logic | M | P-012 | Phase 3 orchestration section |
| T4.9 | Author fix proposal agent prompt template with 3 enforced tiers | M | P-010 | Phase 3 agent prompt |
| T4.10 | Author `test_requirements` structure with unit/integration/e2e classification | S | (FR-019) | test_requirements section |
| T4.11 | Author Phase 3 three-level token budget | S | P-012 | Phase 3 token budget |
| T4.12 | Author Phase 3 MCP routing (Serena, Context7) | S | P-014 | Phase 3 MCP section |
| T4.13 | Author Phase 3 checkpoint update instructions | XS | P-008 | Checkpoint section |

**Success Criteria**:

| ID | Criterion | Verification |
|----|-----------|-------------|
| SC-032 | Phase 1 agent prompt produces slug-based hypothesis IDs (`H-{slug}-{seq}`) | prompt review |
| SC-033 | Model tier selection logic uses 0.7 threshold from FR-010 | logic review |
| SC-034 | Phase 1 and Phase 3 each have 3-level token budgets | count check |
| SC-035 | Fix proposal prompt enforces exactly 3 tiers (minimal, moderate, robust) | prompt review |
| SC-036 | Zero-hypothesis handling block is present and references `progress.json` | content review |
| SC-037 | `test_requirements` includes `type` field (unit/integration/e2e) | schema cross-ref |
| SC-038 | Phases 1 and 3 both reference `refs/schemas.md` for output validation | cross-ref check |

**Estimated effort**: L (6-10 days)
**Depends on**: M3 (Phase 0 must be authored; slug IDs established)
**Blocks**: M5

---

## M5: Phases 2+3b Adversarial Integration + Phases 4-6 Pipeline

**Objective**: Author the complete pipeline for the remaining phases: Phase 2 (adversarial
hypothesis debate), Phase 3b (adversarial fix debate), Phase 4 (implementation delegation),
Phase 5 (validation), and Phase 6 (final report). Also authors the checkpoint/resume protocol
and the `--clean` cleanup behavior.

This is the largest authoring milestone. It incorporates P-003 (dry-run), P-011 (orchestrator
fallback), P-014 (MCP contracts), P-017 (baseline test artifact), P-018 (exit criteria),
P-019 (`--clean` behavior), and P-020 (artifact redaction).

**Deliverables**:

| ID | Deliverable | Path | Description |
|----|-------------|------|-------------|
| D5.1 | Phase 2 behavior spec in SKILL.md | SKILL.md §Phase 2 | Adversarial invocation pattern (`Skill sc:adversarial-protocol --compare`), return contract handling, orchestrator hypothesis filtering (confidence threshold), token budget (3-level). |
| D5.2 | Phase 3b behavior spec in SKILL.md | SKILL.md §Phase 3b | Adversarial invocation for fixes, orchestrator fix greenlight decision logic, implementation plan construction, token budget (3-level). |
| D5.3 | Adversarial integration ref | `refs/adversarial-integration.md` | Invocation patterns for Phase 2 and 3b, return contract fields consumed, convergence threshold routing, error handling for adversarial failures. |
| D5.4 | Phase 4 behavior spec in SKILL.md | SKILL.md §Phase 4 | Specialist agent selection logic, implementation prompt (A-4a), regression test creation prompt (A-4b), worktree isolation guidance, changes/new-tests manifest writing. |
| D5.5 | Phase 5 behavior spec in SKILL.md | SKILL.md §Phase 5 | Parallel validation: lint (A-5a Haiku), test execution + analysis (A-5b Sonnet), self-review (A-5c Sonnet). Baseline test artifact (P-017). |
| D5.6 | Phase 6 behavior spec in SKILL.md | SKILL.md §Phase 6 | Final report synthesis prompt, input artifact list (summary only), exit criteria (P-018), `--clean` behavior (P-019). |
| D5.7 | Checkpoint/resume protocol ref | `refs/checkpoint-resume.md` | Full `progress.json` update protocol, phase restart semantics (per spec §12), resume logic, `--resume` flag handling, `phase_status_map` update rules. |
| D5.8 | Artifact redaction ref | `refs/redaction.md` | `--redact` flag behavior (default: true), regex patterns for secrets (API keys, tokens, passwords, private keys), application to all persisted artifacts, redaction log. |
| D5.9 | Exit criteria and `--clean` section | SKILL.md §Exit | Pipeline exit conditions: `success`, `success_with_risks`, `failed`. `--clean` restricted to terminal `success` only. Artifact retention for non-success outcomes. |

**Tasks**:

| ID | Task | Complexity | Proposals | Output |
|----|------|------------|---------|--------|
| T5.1 | Author Phase 2 adversarial invocation pattern and return contract handling | M | (FR-012-016) | Phase 2 spec |
| T5.2 | Author Phase 2 orchestrator hypothesis filtering with confidence threshold | S | (FR-016) | Filtering logic |
| T5.3 | Author Phase 2 three-level token budget | S | P-012 | Phase 2 token budget |
| T5.4 | Author Phase 3b adversarial invocation and fix greenlight decision | M | P-005 | Phase 3b spec |
| T5.5 | Author Phase 3b three-level token budget | S | P-012 | Phase 3b token budget |
| T5.6 | Author orchestrator fallback handling for partial phase results | S | P-011 | Fallback block |
| T5.7 | Author Phase 4 specialist agent selection logic | S | (FR-025, §8.2) | Agent selection |
| T5.8 | Author Agent 4a implementation prompt and Serena usage | M | (FR-026) | A-4a prompt |
| T5.9 | Author Agent 4b regression test creation prompt | M | (FR-027) | A-4b prompt |
| T5.10 | Author worktree isolation guidance for Phase 4 | S | (NFR-008) | Isolation section |
| T5.11 | Author Agent 5a lint validation prompt | S | (FR-030) | A-5a prompt |
| T5.12 | Author Agent 5b test execution + failure analysis prompt | M | (FR-031) | A-5b prompt |
| T5.13 | Author Agent 5b baseline test artifact capture (pre-fix baseline) | S | P-017 | Baseline artifact section |
| T5.14 | Author Agent 5c self-review prompt with 4 mandatory questions | S | (FR-032) | A-5c prompt |
| T5.15 | Author Phase 6 final report synthesis prompt | M | P-018 | Phase 6 prompt |
| T5.16 | Author exit criteria section (success/success_with_risks/failed) | S | P-018 | Exit section |
| T5.17 | Author `--clean` behavior restricted to `success` terminal status | S | P-019 | Clean section |
| T5.18 | Author `refs/adversarial-integration.md` | M | P-005 | adversarial-integration.md |
| T5.19 | Author `refs/checkpoint-resume.md` with strengthened `progress.json` | M | P-008 | checkpoint-resume.md |
| T5.20 | Author `refs/redaction.md` with `--redact` flag and regex patterns | M | P-020 | redaction.md |
| T5.21 | Author `--dry-run` bypass of Phases 4-5 | S | P-003 | Dry-run gate |
| T5.22 | Integrate `--concurrency` note referencing MCP.md per-server limits | XS | P-022 addendum | Concurrency note |

**Success Criteria**:

| ID | Criterion | Verification |
|----|-----------|-------------|
| SC-039 | Phase 2 invocation matches `--compare` pattern in spec §7.2 | cross-ref |
| SC-040 | Phase 3b output contract matches P-005 (`fix-selection.md` schema) | schema cross-ref |
| SC-041 | Orchestrator fallback logs to `progress.json.phase_status_map` | content review |
| SC-042 | Agent 5b captures baseline test results before applying fixes (P-017) | content review |
| SC-043 | Exit criteria section defines all 3 statuses | count check |
| SC-044 | `--clean` is gated on `success` status only | content review |
| SC-045 | `refs/redaction.md` includes regex patterns for at least 4 secret types | content review |
| SC-046 | `refs/checkpoint-resume.md` references `run_id`, `phase_status_map` from P-008 | cross-ref |
| SC-047 | `--dry-run` halts before Phase 4 | logic review |
| SC-048 | `--concurrency` note references MCP.md (P-022 addendum) | content review |

**Estimated effort**: L (6-10 days)
**Depends on**: M4
**Blocks**: M6

---

## M6: Testing, Sync, Verification, and Documentation

**Objective**: Validate the complete `/sc:forensic` implementation through independent per-phase
tests and end-to-end pipeline tests. Run `make sync-dev` and `make verify-sync` to propagate
artifacts to the installed `.claude/` location. Complete inline documentation within all files.

**Testing philosophy**: Tests validate behavioral contracts (do agents produce the right
schema-conforming artifacts?) not internal implementation. Each phase can be tested
independently because it has well-defined inputs (prior phase artifacts) and outputs (new
artifacts). Tests use small codebases (3-5 files) per P-015 smoke test requirement.

**Deliverables**:

| ID | Deliverable | Path | Description |
|----|-------------|------|-------------|
| D6.1 | Phase 0 smoke test | `tests/sprint/forensic/test_phase0_smoke.py` | 3-file codebase fixture; asserts structural-inventory, dependency-graph, risk-surface artifacts are produced and schema-valid. |
| D6.2 | Phase 1 smoke test | `tests/sprint/forensic/test_phase1_smoke.py` | Uses Phase 0 fixture output; asserts findings-domain-{N}.md files have correct hypothesis structure, slug IDs, evidence fields. |
| D6.3 | Phase 3 smoke test | `tests/sprint/forensic/test_phase3_smoke.py` | Uses Phase 2 fixture output (canned); asserts fix-proposal files have exactly 3 tiers, test_requirements present. |
| D6.4 | Phase 5 smoke test | `tests/sprint/forensic/test_phase5_smoke.py` | Uses Phase 4 fixture output (canned); asserts lint-results.txt, test-results.md, self-review.md all present. |
| D6.5 | Checkpoint/resume integration test | `tests/sprint/forensic/test_checkpoint_resume.py` | Simulates Phase 0-2 completion, writes progress.json, invokes `--resume`, asserts pipeline continues from Phase 3. Validates `run_id` stability, `phase_status_map` updates. |
| D6.6 | Zero-hypothesis edge case test | `tests/sprint/forensic/test_zero_hypotheses.py` | Injects canned Phase 2 output with 0 surviving hypotheses; asserts graceful halt, empty-result artifact, no Phase 3 spawn. |
| D6.7 | Tiny target smoke test | `tests/sprint/forensic/test_tiny_target.py` | 3-file target; asserts single-domain output from Phase 0, bypassed domain auto-discovery. |
| D6.8 | `--dry-run` behavioral test | `tests/sprint/forensic/test_dry_run.py` | Asserts pipeline halts after Phase 3b, no Phase 4-5 artifacts produced. |
| D6.9 | `--redact` flag test | `tests/sprint/forensic/test_redaction.py` | Injects artifact with synthetic secret patterns; asserts patterns are redacted in output. |
| D6.10 | Schema conformance test suite | `tests/sprint/forensic/test_schemas.py` | Validates all 9 schemas against sample JSON fixtures. Checks required fields, type constraints, slug format. |
| D6.11 | Sync verification | CI gate | `make sync-dev && make verify-sync` exits 0. |
| D6.12 | SKILL.md completeness review | Manual | All 7 phase sections filled (no stubs). All refs present. Return contract documented. |
| D6.13 | Command file review | Manual | All 10 flags present with correct defaults. Activation block correct. Boundaries accurate. |

**Tasks**:

| ID | Task | Complexity | Proposals | Output |
|----|------|------------|---------|--------|
| T6.1 | Author Phase 0 smoke test fixture and assertions | M | P-015 | test_phase0_smoke.py |
| T6.2 | Author Phase 1 smoke test | M | P-015 | test_phase1_smoke.py |
| T6.3 | Author Phase 3 smoke test with 3-tier enforcement check | S | P-010, P-015 | test_phase3_smoke.py |
| T6.4 | Author Phase 5 smoke test | S | P-015, P-017 | test_phase5_smoke.py |
| T6.5 | Author checkpoint/resume integration test | M | P-008 | test_checkpoint_resume.py |
| T6.6 | Author zero-hypothesis edge case test | S | P-016 | test_zero_hypotheses.py |
| T6.7 | Author tiny target smoke test | S | P-015 | test_tiny_target.py |
| T6.8 | Author `--dry-run` behavioral test | S | P-003 | test_dry_run.py |
| T6.9 | Author `--redact` flag test with secret pattern fixtures | M | P-020 | test_redaction.py |
| T6.10 | Author schema conformance test suite (all 9 schemas) | L | P-006–P-009, P-021 | test_schemas.py |
| T6.11 | Run `make sync-dev` | XS | — | Sync .claude/ |
| T6.12 | Run `make verify-sync` and resolve any mismatches | XS | — | Sync confirmation |
| T6.13 | Full SKILL.md completeness pass (no stubs, all refs linked) | M | all | Reviewed SKILL.md |
| T6.14 | Full command file review against amended spec | S | all | Reviewed forensic.md |
| T6.15 | Run full test suite: `uv run pytest tests/sprint/forensic/ -v` | S | P-015 | Test results |
| T6.16 | Address any test failures and iterate | M | — | Passing test suite |

**Success Criteria**:

| ID | Criterion | Verification |
|----|-----------|-------------|
| SC-049 | All smoke tests pass on 3-5 file codebase fixture | `uv run pytest tests/sprint/forensic/ -v` |
| SC-050 | Checkpoint/resume test validates `run_id` stability and `phase_status_map` | test pass |
| SC-051 | Zero-hypothesis test confirms graceful halt (no Phase 3 artifacts) | test pass |
| SC-052 | `--redact` test confirms at least 4 secret pattern types are redacted | test pass |
| SC-053 | Schema conformance test passes all 9 schemas | test pass |
| SC-054 | `make verify-sync` exits 0 | CI check |
| SC-055 | SKILL.md contains no stub sections | manual review |
| SC-056 | Command file contains activation block, all 10 flags, boundaries | manual review |
| SC-057 | All test files located under `tests/sprint/forensic/` | directory check |
| SC-058 | Tiny target test produces single-domain output | test pass |

**Estimated effort**: L (6-10 days)
**Depends on**: M5
**Blocks**: release

---

## Risk Register

| ID | Risk | Category | Probability | Impact | Exposure | Mitigation |
|----|------|----------|-------------|--------|----------|------------|
| R-001 | sc:adversarial-protocol API changes break Phase 2/3b invocation | External dependency | 2 | 5 | 10 (Medium) | Lock invocation pattern against current skill version. Document exact `--compare` flag contract. Test with canned adversarial outputs to decouple. |
| R-002 | Slug-based domain IDs (P-009) not stable across pipeline reruns for edge-case domain names | Architecture | 2 | 4 | 8 (Medium) | Define slugification algorithm explicitly in `refs/schemas.md`. Include normalization rules (lowercase, replace spaces/special chars with `-`, deduplicate). |
| R-003 | Three-level token budget hard ceilings (P-012) are set too low for large codebases | Feasibility | 3 | 3 | 9 (Medium) | Set hard ceilings at 2x empirically-observed soft targets from existing adversarial runs. Include overflow-action guidance for agent self-truncation. |
| R-004 | Phase 0 produces > 10 domains for very large codebases, violating schema constraint | Edge case | 2 | 3 | 6 (Low) | Spec explicitly caps domains at 10. Add orchestrator instruction to merge related domains when > 10 discovered. |
| R-005 | `make verify-sync` fails due to inconsistent line endings or metadata differences between src/ and .claude/ | CI / tooling | 2 | 2 | 4 (Low) | Run `make sync-dev` before `make verify-sync`. Investigate existing verify-sync implementation to understand comparison method. |
| R-006 | `--redact` (P-020) regex patterns produce false positives on legitimate code | Security | 2 | 3 | 6 (Low) | Use conservative patterns (API key prefixes, explicit token formats). Provide opt-out mechanism via `--redact false`. Document known false-positive patterns. |
| R-007 | Checkpoint resume (P-008) `run_id` collisions across concurrent forensic runs | Architecture | 1 | 4 | 4 (Low) | Use UUID v4 for `run_id`. Document that concurrent runs must use different `--output` directories. |
| R-008 | Adversarial protocol convergence failures (convergence < 0.80) in Phase 2 cause pipeline halt | Pipeline | 3 | 4 | 12 (Medium) | Per P-011, implement partial-result continuation: if convergence < threshold but > 0.5, proceed with surviving hypotheses and log warning. Only hard-abort below 0.5. |
| R-009 | Scope creep: request to add non-planned features during authoring | Process | 3 | 2 | 6 (Low) | Strict scope gate: only implement what is specified in the amended spec. New ideas → backlog as v2 candidates. |
| R-010 | SKILL.md grows too large to load efficiently in context | Performance | 2 | 3 | 6 (Low) | Use refs/ pattern (established by sc:roadmap-protocol). Move phase-specific prompts to dedicated ref files. SKILL.md contains only routing and orchestration logic. |

---

## Decision Summary

| Decision | Rationale | Alternative Considered | Rejected Because |
|----------|-----------|----------------------|-----------------|
| Generate roadmap v2 with `-2` suffix (collision protocol) | Output directory already contains prior artifacts from 2026-02-26 run | Overwrite existing | Overwrites prior planning artifacts, violates collision protocol |
| Apply all 21 proposals as M0-M1 spec amendments before authoring | Structural and schema issues in the spec would propagate into all authoring; cost of mid-stream correction is 3-5x | Incorporate inline during authoring | Creates moving-target problem; parallel contributors would diverge |
| Split M0 (Tier 1) from M1 (Tiers 2-3) into separate milestones | Tier 1 proposals fix normative markers and path conventions — blockers that Tier 2-3 authors depend on | Single spec amendment milestone | A single large amendment milestone delays all authoring by one full milestone; splitting enables M1 to begin while M0 is being reviewed |
| Use refs/ pattern for phase prompts | Established pattern from sc:cleanup-audit-protocol and sc:roadmap-protocol; keeps SKILL.md focused on routing | Inline all prompts in SKILL.md | SKILL.md would exceed practical context loading limits |
| 7 milestones (vs 9 in prior roadmap) | Fewer, larger milestones reduce coordination overhead; M3-M5 were granular enough to author but too fine for milestone tracking | 9 milestones (prior roadmap) | Excessive granularity; phases 1 and 3 share enough structural similarity to author within a single milestone (M4) |
| Testing in `tests/sprint/forensic/` | Follows existing `tests/sprint/` directory pattern | `tests/forensic/` | Inconsistent with current test organization conventions |
| P-022 (MCP scheduling) incorporated as note only | Rejected by adversarial debate (convergence 0.76); framework-level concern | Full specification | Duplicates MCP.md circuit breaker logic; creates maintenance conflict |

---

## Cross-Milestone Proposal Integration Map

This table maps every accepted/modified proposal to its primary milestone and tasks.

| Proposal | Verdict | Milestone | Primary Tasks |
|---------|---------|-----------|--------------|
| P-001 (normative markers) | ACCEPT | M0 | T0.1 |
| P-002 (`--depth` precedence) | ACCEPT | M0 | T0.4 |
| P-003 (`--dry-run` phase plan) | ACCEPT | M0 (flag spec) + M5 (behavior) | T0.4, T5.21 |
| P-004 (path standardization) | ACCEPT | M0 | T0.2 |
| P-005 (Phase 3b output contract) | ACCEPT | M0 | T0.3 |
| P-006 (new-tests-manifest schema) | ACCEPT | M1 | T1.1 |
| P-007 (risk surface alignment) | MODIFY | M1 (schema) + M3 (behavior) | T1.2, T3.3 |
| P-008 (progress.json strengthening) | MODIFY | M1 (schema) + M5 (behavior) | T1.4, T5.19 |
| P-009 (stable domain IDs) | MODIFY | M1 (spec-wide) + M3/M4 (behavior) | T1.5, T3.4, T4.3 |
| P-010 (fix tier enforcement) | ACCEPT | M1 (schema) + M4 (behavior) | T1.3, T4.9 |
| P-011 (orchestrator fallback) | ACCEPT | M1 (spec) + M5 (behavior) | T1.10, T5.6 |
| P-012 (three-level token budgets) | MODIFY | M1 (spec) + M3/M4/M5 (behavior) | T1.9, T3.5, T4.4, T4.11, T5.3, T5.5 |
| P-013 (model-tier fallback) | ACCEPT | M0 | T0.5 |
| P-014 (MCP tool contract) | ACCEPT | M1 (spec) + M3/M4/M5 (behavior) | T1.7, T3.8, T4.5, T4.12 |
| P-015 (tiny target handling) | ACCEPT | M1 (spec) + M3 (behavior) + M6 (tests) | T1.8, T3.4, T6.7 |
| P-016 (zero-hypothesis handling) | ACCEPT | M1 (spec) + M4 (behavior) + M6 (tests) | T1.12, T4.7, T6.6 |
| P-017 (baseline test artifact) | ACCEPT | M5 | T5.13 |
| P-018 (exit criteria) | ACCEPT | M5 | T5.15, T5.16 |
| P-019 (`--clean` behavior) | MODIFY | M5 | T5.17 |
| P-020 (artifact redaction) | MODIFY | M5 (behavior) + M6 (tests) | T5.20, T6.9 |
| P-021 (multi-root provenance) | MODIFY | M1 (schema) + M3 (behavior) | T1.6, T3.1 |
| P-022 (MCP concurrency) | REJECT | M5 (addendum note only) | T5.22 |

---

## Next Steps

This roadmap is a planning artifact. Implementation begins when this document has been reviewed
and approved.

**Recommended initiation sequence**:

1. Review and approve this roadmap (user action)
2. Begin M0: spec amendment tasks T0.1-T0.6 (3-5 days)
3. Upon M0 review approval, begin M1 in parallel with M0 final review (T1.1-T1.14)
4. Upon M1 completion, begin M2 authoring (command shell + skill shell + schemas)
5. Continue sequentially through M3 → M4 → M5 → M6

**Artifacts produced by this roadmap** (not by the roadmap's downstream tasks):
- This file: `roadmap-2.md`
- `extraction-2.md` (requirements and complexity analysis)
- `test-strategy-2.md` (validation strategy)

The tasklist command (if used) should reference `M0.T0.1` through `M6.T6.16` task IDs.
