---
feature: /sc:forensic + sc:forensic-protocol
artifact: dependency-graph
date: 2026-02-26
---

# Dependency Graph — /sc:forensic Implementation

This document maps the dependency relationships between roadmap milestones and between the forensic pipeline's internal phases. Two views are provided: milestone dependencies (implementation order) and pipeline phase dependencies (runtime data flow).

---

## Milestone Dependency Graph

The following shows which milestones must be fully complete before a downstream milestone can begin.

```
M0 (Tier 1-2 Spec Amendments)
│  P-001 Section 17 integration
│  P-004 artifact path fix
│  P-009 domain ID stability
│  P-006 new-tests-manifest schema
│  P-013 model tier tracking
│  P-015 min-domain rule
│  P-014 tool contract alignment
│  P-021 multi-root provenance
│
└──► M1 (Tier 3-5 Spec Amendments)
     │  P-017 baseline test artifact
     │  P-018 exit state model
     │  P-003 dry-run/skipped_phases
     │  P-002 --depth precedence
     │  P-005 phase-3b canonical path
     │  P-011 adversarial fallback chain
     │  P-012 token overflow policy
     │  P-020 artifact redaction
     │  P-016 zero-hypothesis terminal
     │  P-022 MCP budgets / concurrency default
     │  P-007 risk surface alignment (partial)
     │  P-010 fix tier uniqueness (partial)
     │  P-008 progress.json hardening (partial)
     │  P-019 --clean guard clause
     │
     └──► M2 (Foundation: Command, Skill Shell, Schemas)
          │  forensic.md (command)
          │  sc-forensic-protocol/SKILL.md (shell)
          │  sc-forensic-protocol/schemas.md
          │  sc-forensic-protocol/rules/ (stubs)
          │
          └──► M3 (Checkpoint/Resume Protocol)
               │  progress.json writer
               │  resume validation logic
               │  artifact directory tree
               │  --clean guard clause
               │
               └──► M4 (Phase 0: Reconnaissance)
                    │  Agent 0a: structural inventory
                    │  Agent 0b: dependency graph
                    │  Agent 0c: risk surface scan
                    │  Orchestrator: domain generation
                    │
                    └──► M5 (Phase 1 + Phase 3: Discovery & Fix Proposals)
                         │  Phase 1: investigation agent template
                         │  Phase 1: orchestrator collection
                         │  Phase 3: fix proposal agent template
                         │  Phase 3: orchestrator collection
                         │  Parallel dispatch pattern
                         │
                         └──► M6 (Adversarial Integration: Phase 2 + Phase 3b)
                              │  Phase 2: adversarial invocation pattern    ◄── /sc:adversarial (external)
                              │  Phase 2: hypothesis filtering + zero-hypothesis path
                              │  Phase 3b: adversarial invocation pattern
                              │  Phase 3b: fix greenlight decision
                              │
                              └──► M7 (Phase 4 + Phase 5: Implementation + Validation)
                                   │  Phase 4: baseline test capture
                                   │  Phase 4: Agent 4a code fix specialist
                                   │  Phase 4: Agent 4b regression test creator
                                   │  Phase 4: redaction pass
                                   │  Phase 5: Agent 5a lint
                                   │  Phase 5: Agent 5b test execution + baseline diff
                                   │  Phase 5: Agent 5c self-review
                                   │  Phase 5: exit state determination
                                   │  Phase 5: redaction pass
                                   │
                                   └──► M8 (Phase 6 + CLI Integration)
                                        │  Phase 6: orchestrator synthesis
                                        │  Final report template
                                        │  Final report redaction pass
                                        │  Command discovery integration
                                        │
                                        └──► M9 (Testing + Documentation) ──► RELEASE
```

---

## Critical Path

The critical path is the longest sequential chain of milestones:

```
M0 → M1 → M2 → M3 → M4 → M5 → M6 → M7 → M8 → M9
```

All milestones are on the critical path because the dependency graph is linear. There are no milestones that can be parallelized with other milestones (each milestone provides the spec foundation or artifacts consumed by the next).

**Within individual milestones**, parallelization is possible:
- M0/M1: Individual proposal integrations are largely independent after P-001 (Section 17 integration) establishes the baseline. Tasks within M0 (T-M0-2 through T-M0-8) and M1 (T-M1-1 through T-M1-14) can be executed in parallel once T-M0-1 is complete.
- M4: The 3 Phase 0 recon agents (T-M4-1, T-M4-2, T-M4-3) are specified in parallel. They are independent of each other.
- M5: Phase 1 investigation agents and Phase 3 fix-proposal agents can be designed in parallel.
- M7: Phase 4 (T-M7-1 baseline capture → then T-M7-2 and T-M7-3 in parallel) and Phase 5 (T-M7-5, T-M7-6, T-M7-7 in parallel) contain internal parallelism.
- M9: All testing tasks can be executed in parallel once M8 is complete.

---

## Pipeline Phase Data Flow

This shows the runtime data dependencies between the 7 forensic pipeline phases.

```
Input: [target-paths...]
         │
         ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  PHASE 0: Reconnaissance (3x Haiku parallel)                   │
   │                                                                 │
   │  Agent 0a → phase-0/structural-inventory.json                  │
   │  Agent 0b → phase-0/dependency-graph.json                      │
   │  Agent 0c → phase-0/risk-surface.json                          │
   │         └──────────────────────────────────────────────────►   │
   │  Orchestrator (Opus) reads 3 JSON summaries                     │
   │                → phase-0/investigation-domains.json             │
   └─────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  PHASE 1: Root-Cause Discovery (N x Sonnet/Haiku parallel)     │
   │                                                                 │
   │  Investigation domains → N parallel agents                      │
   │  Each agent reads: domain definition + struct-inv + dep-graph   │
   │  Agent 1-N → phase-1/findings-domain-{N}.md                    │
   │                                                                 │
   │  Orchestrator: collects file paths only (~1,000 tokens)         │
   └─────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  PHASE 2: Adversarial Debate — Hypotheses (delegated)          │
   │                                                                 │
   │  Delegates to: /sc:adversarial --compare findings-domain-*.md  │
   │  Adversarial protocol runs its full 5-step pipeline             │
   │  → phase-2/adversarial/debate-transcript.md                    │
   │  → phase-2/adversarial/base-selection.md                       │
   │                                                                 │
   │  Orchestrator: reads base-selection.md summary scores only      │
   │    → applies confidence threshold filter                        │
   │    → zero hypotheses? → terminal report                         │
   │    → surviving hypothesis cluster IDs passed to Phase 3         │
   └─────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  PHASE 3: Fix Proposals (M x Sonnet parallel)                  │
   │                                                                 │
   │  One Sonnet agent per surviving hypothesis cluster              │
   │  Agent 3-M → phase-3/fix-proposal-H-{id}-{seq}.md              │
   │                                                                 │
   │  Orchestrator: collects proposal file paths                     │
   └─────────────────────────────────────┬───────────────────────────┘
                                         │
                                         ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  PHASE 3b: Adversarial Debate — Fixes (delegated)              │
   │                                                                 │
   │  Delegates to: /sc:adversarial --compare fix-proposal-*.md     │
   │  → phase-3b/fix-selection.md                                   │
   │                                                                 │
   │  Orchestrator: reads fix-selection.md summary                   │
   │    → selects fix tiers per --fix-tier flag                      │
   │    → greenlights fixes                                          │
   │    → assigns specialist agents                                  │
   │  PRIMARY DECISION POINT                                         │
   └─────────────────────────────────────┬───────────────────────────┘
                                         │
                  ┌──────────────────────┴──────────────────────┐
                  │                                             │
                  ▼                                             ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  PHASE 4: Implementation (2 Sonnet parallel)                 │
   │                                                              │
   │  Pre-implementation: capture baseline test results           │
   │  → phase-4/baseline-test-results.md                         │
   │                                                              │
   │  Agent 4a (specialist): reads fix-selection.md               │
   │    → phase-4/changes-manifest.json                          │
   │                                                              │
   │  Agent 4b (quality-engineer): reads test_requirements        │
   │    → phase-4/new-tests-manifest.json                        │
   │                                                              │
   │  Post-write: redaction pass on all Phase 4 artifacts         │
   └─────────────────────────────┬────────────────────────────────┘
                                 │
         ┌───────────────────────┼──────────────────────┐
         │                       │                      │
         ▼                       ▼                      ▼
   ┌──────────────┐  ┌────────────────────────┐  ┌────────────────────┐
   │ PHASE 5a     │  │ PHASE 5b               │  │ PHASE 5c           │
   │ Lint Pass    │  │ Test Execution         │  │ Self-Review        │
   │ (Haiku)      │  │ (Sonnet/quality-eng)   │  │ (Sonnet/self-rev)  │
   │              │  │                        │  │                    │
   │ lint-results │  │ test-results.md        │  │ self-review.md     │
   │ .txt         │  │ (with introduced vs    │  │                    │
   │              │  │  preexisting failures) │  │                    │
   └──────────────┘  └────────────────────────┘  └────────────────────┘
         │                       │                      │
         └───────────────────────┴──────────────────────┘
                                 │
                                 ▼
                    Exit state determination:
                    success / success_with_risks / failed
                                 │
                                 ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  PHASE 6: Final Report (Opus)                                   │
   │                                                                 │
   │  Reads ONLY (6 summary artifacts):                              │
   │    phase-0/investigation-domains.json                           │
   │    phase-2/adversarial/base-selection.md                        │
   │    phase-3b/fix-selection.md                                    │
   │    phase-5/lint-results.txt                                     │
   │    phase-5/test-results.md                                      │
   │    phase-5/self-review.md                                       │
   │                                                                 │
   │  → phase-6/final-report.md                                      │
   │    (includes YAML frontmatter with exit_status)                 │
   │                                                                 │
   │  Post-write: redaction pass on final-report.md                  │
   └─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                           Output: phase-6/final-report.md
                           Checkpoint: progress.json (all phases completed)
```

---

## External Dependencies

| Dependency | Type | Required By | Risk |
|------------|------|-------------|------|
| `/sc:adversarial` command (operational) | Runtime | M6 (Phase 2, Phase 3b) | R-01 (HIGH) |
| `sc:adversarial-protocol` skill (loadable) | Runtime | M6 via adversarial delegation | R-01 (HIGH) |
| Serena MCP server | Optional (with fallback) | M4 (Agent 0b), M5 (Phases 1, 3), M7 (Phase 4a) | R-04 (LOW) |
| Context7 MCP server | Optional (with fallback) | M5 (Phases 1, 3), M7 (Phase 4b) | R-04 (LOW) |
| Sequential MCP server | Optional (with fallback) | M5 (Phase 1 reasoning) | R-04 (LOW) |
| Haiku/Sonnet/Opus model availability | Runtime | All phases | R-02 (MEDIUM) |
| `uv run ruff check` (lint tool) | Runtime | M7 (Phase 5a) | Low |
| `uv run pytest` (test runner) | Runtime | M7 (Phase 4 baseline, Phase 5b) | Low |

---

## Proposal Integration Dependencies

Within M0 and M1, the following proposal-to-proposal dependencies exist:

```
P-001 (Section 17 integration)
  └──► ALL other proposals
       (establishes true spec baseline before any section editing)

P-017 (baseline test artifact)
  └──► P-018 (exit state model)
         └──► P-019 (--clean guard clause references "successful completion")

P-020 (artifact redaction)
  └──► P-017 (baseline test results are also artifacts needing redaction)

P-009 (domain ID stability)
  └──► P-021 (multi-root provenance — path records reference domain_id)
```

All other proposals within M0/M1 are independent and can be applied in parallel after P-001 establishes the baseline.
