# PRD — Deterministic Tasklist Generation Pipeline for Sprint CLI

## 1) Problem Statement
The current release workflow can produce high-quality roadmap-derived tasklists, but execution reliability depends on consistent packaging into sprint-compatible artifacts (`tasklist-index.md` + canonical phase files) and clear command ownership between planning/orchestration and compliance/execution.

Without a deterministic handoff and severity policy, teams face:
- inconsistent generated artifacts,
- unclear ownership between `/sc:workflow` and `/sc:task-unified`,
- avoidable execution friction from warning handling ambiguity.

## 2) Goals
1. Ensure deterministic transformation from roadmap intent to sprint-executable task artifacts.
2. Preserve clean command boundaries:
   - `/sc:workflow` = orchestration/planning/generation pipeline control
   - `/sc:task-unified` = task compliance/execution behavior
3. Standardize execution gate behavior:
   - block on **dry-run errors**
   - do not block on warnings by default
   - allow strict mode for warning-blocking environments.
4. Improve auditability and reproducibility across releases.

## 3) Adjudicated Decisions

### D1 — Output Strategy (Accepted)
**Decision:** Generator outputs **only `tasklist.md`**. A deterministic compiler emits:
- `tasklist-index.md`
- canonical phase files

**Confidence:** 0.82

### D2 — Command Ownership (Accepted)
**Decision:** Keep `/sc:workflow` as orchestrator. `/sc:task-unified` remains compliance/execution layer.

**Confidence:** 0.79

### D3 — Dry-Run Gate Policy (Accepted)
**Decision:** Block execution on **errors only** (not all warnings).

**Confidence:** 0.82

## 4) In Scope
- Prompt/workflow contract updates for generation pipeline.
- Deterministic compiler stage design and acceptance criteria.
- Handoff contract between `/sc:workflow` and `/sc:task-unified`.
- Severity model and dry-run gate policy, including strict mode.
- Rollout and validation plan.

## 5) Out of Scope
- Replacing sprint runtime executor internals.
- Redesigning `/sc:task-unified` tier algorithm itself.
- Dynamic runtime scheduling or auto-priority optimization.
- New UI/TUI features beyond existing sprint tooling.

## 6) End-to-End Architecture / Flow

```text
Spec
  -> Roadmap
    -> (via /sc:workflow + Tasklist Generator Prompt)
      -> tasklist.md (single canonical intent artifact)
        -> Deterministic Compiler
          -> tasklist-index.md
          -> phase-<N>-tasklist.md (or canonical equivalent)
          -> packaging/trace metadata
            -> sprint dry-run validation
              -> if errors: block
              -> if warnings: continue by default (+ log)
                -> sprint execution
                  -> per-phase /sc:task-unified execution
```

## 7) Functional Requirements

### FR-1 Canonical Generator Output
Generator MUST emit exactly one canonical intent file: `tasklist.md`.

### FR-2 Deterministic Compiler Output
Compiler MUST transform `tasklist.md` into sprint-executable artifacts:
- `tasklist-index.md`
- phase files using canonical naming accepted by sprint config discovery

### FR-3 Deterministic Rebuild
Given identical `tasklist.md` + compiler version, output artifacts MUST be byte-stable (or semantically identical under normalized whitespace rules).

### FR-4 Command Boundary Enforcement
`/sc:workflow` MUST own orchestration and pipeline sequencing.
`/sc:task-unified` MUST own tier/compliance behavior during execution tasks.

### FR-5 Handoff Contract
A versioned handoff contract MUST be produced from `/sc:workflow` and consumed by compiler/execution stages. Required fields:
- release identifier
- roadmap item IDs
- task IDs + phase mapping
- dependency references
- tier/confidence metadata
- artifact root paths

### FR-6 Dry-Run Gate
Execution MUST block on dry-run **errors**.
Warnings MUST be surfaced and logged, but not block by default.

### FR-7 Strict Mode
Pipeline MUST support strict gate mode (warning-blocking) for regulated/high-risk runs.

### FR-8 Traceability
Every executable task MUST retain trace links: Roadmap item -> Task -> Deliverable -> Artifact paths.

## 8) Non-Functional Requirements
- **Determinism:** repeatable outputs under same inputs/version.
- **Auditability:** complete trace from source roadmap to execution artifacts.
- **Reliability:** fail-fast on invalid contracts or missing required fields.
- **Maintainability:** clear separation of generation vs compilation vs execution.
- **Operator Clarity:** unambiguous command ownership and failure messaging.

## 9) Contract: `/sc:workflow` <-> `/sc:task-unified`

## 9.1 Ownership
- `/sc:workflow`: orchestrates generation and packaging stages.
- `/sc:task-unified`: executes individual tasks with compliance-tiered behavior.

## 9.2 Required Interface Guarantees
- `/sc:workflow` outputs valid, versioned tasklist contract artifacts.
- Compiler validates contract before emitting execution files.
- Execution stage passes tasks to `/sc:task-unified` without mutating tier metadata unless explicitly overridden.

## 9.3 Compatibility Rules
- Contract schema version must be explicit.
- Consumer must reject unknown-breaking versions.
- Producer must not emit incomplete required fields.

## 10) Severity Model and Gate Policy

## 10.1 Severity Definitions
- **Error:** invariant-breaking condition; execution unsafe or undefined.
- **Warning:** non-blocking risk/advisory; execution possible with operator awareness.

## 10.2 Default Gate
- Errors: block
- Warnings: do not block; log + expose in summary

## 10.3 Escalation
Specific warning classes may be promoted to errors by policy (e.g., security/data-integrity classes).

## 10.4 Strict Mode
When strict mode is enabled:
- warnings become blocking
- run requires explicit pass state (no warnings/errors)

## 11) Acceptance Criteria

1. Generator emits `tasklist.md` only; no direct phase/index artifact generation.
2. Compiler produces valid `tasklist-index.md` and canonical phase files.
3. Sprint dry-run passes on generated artifacts for a representative release sample.
4. Default gate blocks on errors only; warning-only dry-run proceeds.
5. Strict mode blocks on warnings.
6. Traceability matrix remains complete from roadmap items through deliverables.
7. Contract schema validation catches malformed handoffs deterministically.
8. Command docs explicitly state ownership boundaries.

## 12) Rollout Plan

### Phase R1 — Contract + Prompt Alignment
- update wrapper/generator prompt references and version path consistency
- enforce single-output generator contract (`tasklist.md`)

### Phase R2 — Compiler Introduction
- implement deterministic compiler stage
- add schema validation + deterministic output checks

### Phase R3 — Gate Policy Activation
- activate dry-run errors-only blocking
- implement strict mode toggle

### Phase R4 — Validation + Harden
- run sampled releases through end-to-end pipeline
- monitor warning/error distributions and reclassify where needed

## 13) Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Compiler introduces new failure point | Medium | fail-fast diagnostics + contract tests + deterministic fixtures |
| Contract drift between producer/consumer | High | versioned schema + compatibility checks + CI contract tests |
| Warning debt accumulation | Medium | warning budgets, escalation classes, periodic reclassification |
| User confusion over command boundaries | Medium | explicit docs + examples + ownership section in CLI guide |
| Partial artifact inconsistencies | High | atomic write strategy + consistency checks across index/phase files |

## 14) Open Questions (Unresolved Only)
1. Where should the deterministic compiler live long-term (new CLI subcommand vs internal `/sc:workflow` stage implementation detail)?
2. What is the initial strict mode activation policy (manual flag only vs environment/profile default)?
3. Which warning classes are promoted to errors at launch (initial policy table)?

## 15) Current Process Context
Current workflow uses `/sc:workflow` with:
`/config/workspace/SuperClaude_Framework/.dev/releases/TasklistGenPrompt.md`
with release-specific placeholders for roadmap/spec/destination paths.

This PRD formalizes evolution of that flow to deterministic single-output generation + compiler packaging + explicit gate policy.
