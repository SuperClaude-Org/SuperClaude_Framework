---
feature: /sc:forensic + sc:forensic-protocol
spec_source: .dev/releases/backlog/forensic/forensic-spec.md
verdicts_source: .dev/releases/backlog/forensic/adversarial/proposal-verdicts.md
extraction_version: 2.0.0
date: 2026-02-28
complexity_score: 0.87
complexity_class: HIGH
domain_count: 6
primary_domains: [orchestration, agents, schema, testing, security, integration]
requirement_count: 65
  functional: 46
  non_functional: 10
  proposal_derived: 9
persona_activation:
  primary: architect
  supporting: [analyzer, qa, security]
collision_suffix: "-2"
---

# /sc:forensic — Requirements Extraction and Analysis

## Extraction Summary

| Category | Count | Source |
|----------|-------|--------|
| Functional Requirements (original spec) | 46 | forensic-spec.md §3.1 |
| Non-Functional Requirements (original spec) | 10 | forensic-spec.md §3.2 |
| Proposal-Derived Requirements | 9 | proposal-verdicts.md (new FRs from P-003, P-007-P-016, P-018-P-021) |
| Total Requirements | 65 | — |
| Data Schemas | 9 | spec §9 (amended by M0-M1 proposals) |
| Agent Roles | 14 | spec §8.1 agent roster |
| Pipeline Phases | 7 | spec §7 (Phase 0 through Phase 6) |
| Command Flags | 10 | spec §5.3 |

---

## Domain Analysis

### Domain 1: Orchestration and Pipeline Control

**Keywords**: orchestrator, phase transition, checkpoint, resume, progress.json, token budget,
fan-out, fan-in, concurrency limit, dry-run, exit criteria

**Requirements mapped**: FR-006, FR-011, FR-016, FR-024, FR-033, FR-035, FR-043-046, NFR-001,
NFR-003, NFR-005, NFR-006, NFR-007 + P-002, P-003, P-008, P-011, P-012, P-018, P-019

**Complexity signals**:
- Multi-phase state machine with 7 states and 3 exit statuses
- Checkpoint protocol requires consistent state across session interruptions
- Token budget enforcement requires 3-level policy per phase (P-012)
- Orchestrator must read ONLY summary artifacts (architectural constraint, not just preference)
- Resume logic requires artifact integrity validation (missing artifact → demote phase)

**Complexity score**: 0.90 (VERY HIGH)

### Domain 2: Agent Architecture and Model Tiering

**Keywords**: model tier, haiku, sonnet, opus, agent selection, specialist agent, investigation
agent, root-cause-analyst, quality-engineer, self-review, python-expert, backend-architect,
debate-orchestrator

**Requirements mapped**: FR-001-005, FR-007-011, FR-017, FR-025-029, FR-030-032, FR-046 +
P-007, P-009, P-010, P-013, P-014, P-015

**Complexity signals**:
- Dynamic agent count (3-10 domains, variable Phase 1 agents)
- Risk-score-based model tier selection (0.7 threshold for Haiku→Sonnet)
- Model-tier fallback chain when tier unavailable (P-013)
- 14 distinct agent roles across 7 phases
- Worktree isolation requirement for parallel Phase 4 agents

**Complexity score**: 0.85 (HIGH)

### Domain 3: Data Schemas and Artifact Contracts

**Keywords**: schema, json, yaml, structural-inventory, dependency-graph, risk-surface,
investigation-domains, hypothesis, fix-proposal, changes-manifest, new-tests-manifest,
progress, slug, domain_id, target_root, run_id, phase_status_map

**Requirements mapped**: FR-002-004, FR-009, FR-015, FR-018-019, FR-023, FR-028 +
P-006, P-007, P-008, P-009, P-010, P-021

**Complexity signals**:
- 9 distinct JSON/YAML schemas with cross-phase referential integrity
- Slug-based stable IDs must be deterministic across reruns (P-009)
- Conditional required fields (git_head only required for git repos per P-008)
- `fix_options` must have exactly 3 entries (P-010 — hard constraint)
- `target_root` at domain level enables multi-root path resolution (P-021)

**Complexity score**: 0.80 (HIGH)

### Domain 4: Adversarial Protocol Integration

**Keywords**: sc:adversarial, adversarial-protocol, convergence, debate-transcript,
base-selection, fix-selection, --compare, Mode A, convergence threshold, return contract

**Requirements mapped**: FR-012-016, FR-021-024 + P-002, P-005, P-011

**Complexity signals**:
- Runtime dependency on external skill with its own invocation contract
- Two separate adversarial invocations (Phase 2: hypotheses, Phase 3b: fixes)
- Different `--depth` parameters per invocation (deep vs standard)
- Return contract must be handled for failure cases (convergence < threshold)
- Phase 3b output contract is explicitly defined by P-005 as `fix-selection.md`

**Complexity score**: 0.78 (HIGH)

### Domain 5: Security and Data Redaction

**Keywords**: secrets, redaction, API key, token, password, private key, --redact,
regex pattern, artifact security, sensitive data

**Requirements mapped**: P-020 (primary), FR-045 (output directory)

**Complexity signals**:
- Default-true `--redact` flag means redaction is always-on unless explicitly disabled
- Must apply to ALL persisted artifacts (findings, fix proposals, transcripts, manifests)
- Regex patterns must be conservative (avoid false positives on code)
- Redaction log must be produced for auditability

**Complexity score**: 0.65 (MEDIUM)

### Domain 6: Testing and Quality Validation

**Keywords**: smoke test, end-to-end, schema conformance, baseline test artifact,
zero-hypothesis, tiny target, dry-run, pytest, uv run pytest, lint, ruff,
test_requirements, unit, integration, e2e

**Requirements mapped**: FR-019, FR-030-032 + P-015, P-016, P-017, P-018

**Complexity signals**:
- Per-phase independent testing requires canned fixture artifacts for each phase boundary
- 9 separate test files (10 deliverables including schema suite)
- Baseline test artifact (P-017) requires pre-fix and post-fix test run capture
- Zero-hypothesis edge case is a non-obvious failure mode requiring explicit test

**Complexity score**: 0.70 (HIGH)

---

## Complexity Scoring

**Scoring formula** (5-factor, each 0-1, weighted sum):

| Factor | Weight | Score | Calculation |
|--------|--------|-------|-------------|
| Requirement count (65) | 0.20 | 0.90 | > 50 requirements → 0.9 |
| Domain count (6) | 0.20 | 0.85 | 5-7 domains → 0.85 |
| External dependencies (sc:adversarial-protocol) | 0.25 | 0.80 | 1 required runtime dependency |
| Agent complexity (14 roles, dynamic count) | 0.20 | 0.90 | 10+ agent roles → 0.9 |
| State management (7-phase, checkpoint/resume) | 0.15 | 0.90 | Complex state machine → 0.9 |
| **Weighted total** | 1.00 | **0.87** | HIGH |

---

## Proposal Impact Analysis

All 21 accepted/modified proposals affect the spec before implementation. The 9 proposals that
generate NEW requirements (as opposed to modifying existing text) are:

| Proposal | New Requirement Added | Impact Level |
|---------|----------------------|-------------|
| P-003 | `--dry-run` MUST produce phase plan before agent spawn | Medium |
| P-007 | Agent 0c MUST document `overall_risk_score` rationale | Medium |
| P-008 | `run_id`, `spec_version`, `phase_status_map`, `target_paths` REQUIRED in progress.json | High |
| P-011 | Orchestrator MUST offer continue/abort on partial phase failure | High |
| P-012 | Each phase MUST define soft-target, hard-ceiling, overflow-action | High |
| P-014 | Pipeline MUST verify MCP server availability before Phase 0 | Medium |
| P-015 | <5 file targets MUST bypass domain discovery (single domain) | Medium |
| P-016 | Zero surviving hypotheses MUST produce structured empty-result and halt | Medium |
| P-017 | Agent 5b MUST capture baseline tests before fix application | High |
| P-018 | Pipeline MUST define `success`, `success_with_risks`, `failed` exit statuses | Medium |
| P-019 | `--clean` MUST only execute for `success` terminal status | Medium |
| P-020 | `--redact` flag (default: true) applied to all persisted artifacts | Medium |

---

## Persona Activation Analysis

| Persona | Activation Score | Primary Domain | Commands |
|---------|-----------------|----------------|---------|
| architect | 0.94 | Orchestration, agent architecture, phase pipeline design | M0, M1, M2, M3, M4, M5 |
| analyzer | 0.85 | Requirements extraction, schema cross-reference analysis | M0, M1 |
| qa | 0.82 | Testing strategy, validation phase (Phase 5), smoke tests | M6 |
| security | 0.70 | Redaction policy (P-020), secrets patterns, `--redact` | M1 (D1.8), M5 (T5.20) |

**Primary persona**: architect (highest activation score, broadest applicability)

---

## Pre-Existing Infrastructure Analysis

The following exist in the repository and are consumed but NOT built by this roadmap:

| Component | Path | Usage in /sc:forensic | Status |
|-----------|------|----------------------|--------|
| sc:adversarial-protocol | `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` | Invoked in Phases 2 and 3b | Confirmed present |
| sc:cleanup-audit-protocol | `src/superclaude/skills/sc-cleanup-audit-protocol/SKILL.md` | Pattern reference only (checkpoint) | Confirmed present |
| sc:task-unified-protocol | `src/superclaude/skills/sc-task-unified-protocol/SKILL.md` | Pattern reference only (compliance tiering) | Confirmed present |
| sc:forensic-qa-protocol | `src/superclaude/skills/sc-forensic-qa-protocol/` | Predecessor skill (different scope) | Present but distinct |
| quality-engineer agent | `src/superclaude/agents/` | Phases 4b, 5b | To be verified |
| self-review agent | `src/superclaude/agents/` | Phase 5c | To be verified |

**Note**: The `sc:forensic-qa-protocol` skill in the repository is a prior iteration with a
different scope from the new `sc:forensic-protocol`. They do NOT conflict — they serve
different purposes and have different names.

---

## Deliverable File Map

| Deliverable | Primary Path | Sync Target | Milestone |
|-------------|-------------|-------------|-----------|
| Command file | `src/superclaude/commands/forensic.md` | `.claude/commands/sc/forensic.md` | M2 |
| Skill SKILL.md | `src/superclaude/skills/sc-forensic-protocol/SKILL.md` | `.claude/skills/sc-forensic-protocol/SKILL.md` | M2-M5 |
| refs/schemas.md | `src/superclaude/skills/sc-forensic-protocol/refs/schemas.md` | (sync with SKILL.md) | M2 |
| refs/mcp-routing.md | `src/superclaude/skills/sc-forensic-protocol/refs/mcp-routing.md` | (sync with SKILL.md) | M2 |
| refs/phase0-agents.md | `src/superclaude/skills/sc-forensic-protocol/refs/phase0-agents.md` | (sync with SKILL.md) | M3 |
| refs/phase1-agents.md | `src/superclaude/skills/sc-forensic-protocol/refs/phase1-agents.md` | (sync with SKILL.md) | M4 |
| refs/phase3-agents.md | `src/superclaude/skills/sc-forensic-protocol/refs/phase3-agents.md` | (sync with SKILL.md) | M4 |
| refs/adversarial-integration.md | `src/superclaude/skills/sc-forensic-protocol/refs/adversarial-integration.md` | (sync with SKILL.md) | M5 |
| refs/checkpoint-resume.md | `src/superclaude/skills/sc-forensic-protocol/refs/checkpoint-resume.md` | (sync with SKILL.md) | M5 |
| refs/redaction.md | `src/superclaude/skills/sc-forensic-protocol/refs/redaction.md` | (sync with SKILL.md) | M5 |
| tests (10 files) | `tests/sprint/forensic/test_*.py` | — | M6 |
