

---
total_diff_points: 12
shared_assumptions_count: 14
---

## 1. Shared Assumptions and Agreements

Both variants agree on the following foundational elements:

1. **Two new pipeline steps**: `remediate` (step 10) and `certify` (step 11) added to existing `roadmap run`
2. **`Finding` dataclass fields**: Both specify the same field set (id, severity, dimension, description, location, evidence, fix_guidance, files_affected, status, agreement_category)
3. **Parser strategy**: Primary merged-report parser with fallback to individual reflect reports; deduplication by location within 5 lines, higher severity wins
4. **Interactive prompt placement**: Prompt logic in `execute_roadmap()`, NOT in `execute_pipeline()` — preserving non-interactive contract
5. **4-option prompt**: BLOCKING only, BLOCKING+WARNING, All, Skip remediation
6. **Auto-skip categories**: NO_ACTION_REQUIRED and OUT_OF_SCOPE findings always skipped
7. **File allowlist**: Only `roadmap.md`, `extraction.md`, `test-strategy.md` may be edited
8. **Remediation execution**: `ClaudeProcess` directly (not `execute_pipeline()`), matching `validate_executor.py` pattern
9. **Runtime controls**: 300s timeout, single retry, model inheritance, no session flags
10. **Rollback mechanism**: `.pre-remediate` snapshots with full rollback on any failure
11. **Certification as standard Step**: Runs via `execute_pipeline()`, single pass, no auto-loop
12. **Success criteria**: Both reference SC-001 through SC-008 identically
13. **Architectural constraints**: Pure prompt builders (NFR-004), unidirectional imports (NFR-007), atomic writes via `os.replace()` (NFR-005)
14. **Backward compatibility**: Additive-only state schema changes, existing consumers unaffected

---

## 2. Divergence Points

### D-001: Phase Structure and Count
- **Opus-Architect**: 6 phases (P1–P6), no explicit discovery phase
- **Haiku-Analyzer**: 7 phases (P0–P6), includes Phase 0 "Discovery, Baseline, and Architecture Lock"
- **Impact**: Haiku's P0 front-loads ambiguity resolution (0.5–1 day) before any code. Opus assumes discovery happens implicitly within P1. Haiku's approach reduces rework risk; Opus's approach saves calendar time if the team already understands the codebase.

### D-002: Timeline Estimates
- **Opus-Architect**: 17–24 days total, ~15–20 with overlap
- **Haiku-Analyzer**: 6.75 days baseline, 7–9 working days likely
- **Impact**: A ~2.5x difference. Opus provides conservative per-phase buffers (e.g., P3: 5–7 days vs Haiku P3: 1.5–2 days). This reflects different assumptions about team velocity, review overhead, or whether estimates represent elapsed time vs focused engineering time.

### D-003: Phase 1 Scope — State Schema Inclusion
- **Opus-Architect**: P1 includes state schema extension (`.roadmap-state.json` with remediate/certify entries)
- **Haiku-Analyzer**: State schema extension deferred to Phase 5
- **Impact**: Opus front-loads state design alongside the data model, ensuring downstream phases can write state immediately. Haiku treats state as a late integration concern, which risks discovering schema issues after orchestration is built.

### D-004: Tasklist Generation Timing
- **Opus-Architect**: Tasklist emission (`remediation-tasklist.md`) is a Phase 3 deliverable, produced during remediation orchestration
- **Haiku-Analyzer**: Tasklist generation is a Phase 2 deliverable, produced during scope selection before orchestration begins
- **Impact**: Haiku's approach creates the tasklist as a planning artifact before agents run (serving as an audit trail and gate input). Opus generates it as an output of remediation execution. Haiku's sequencing is more aligned with the spec's intent of tasklist-as-plan.

### D-005: REMEDIATE_GATE Placement
- **Opus-Architect**: Gate defined in Phase 3 as part of step registration
- **Haiku-Analyzer**: Gate defined in Phase 2 alongside tasklist generation
- **Impact**: Haiku ties gate validation to tasklist creation (validate the plan before execution). Opus ties it to step completion (validate after execution). The spec references the gate in the context of tasklist validation, favoring Haiku's placement.

### D-006: Prompt Builder Module Naming
- **Opus-Architect**: `remediate_prompts.py`, `certify_prompts.py` (separate modules)
- **Haiku-Analyzer**: Describes "pure prompt functions" without specifying module names
- **Impact**: Opus provides concrete module structure with import dependency mapping. Haiku leaves implementation flexibility but provides less guidance for downstream tasklist generation.

### D-007: Risk Assessment Depth and Structure
- **Opus-Architect**: 7 risks in tabular format with ID, severity, probability, mitigation, and phase mapping
- **Haiku-Analyzer**: 8 risks split into "High-Priority" (5) and "Secondary" (3) with narrative descriptions
- **Impact**: Haiku's risk analysis is more thorough — it explicitly calls out "stale resume causing invalid certification" and "certification false passes" as high-priority risks with detailed mitigation. Opus covers similar ground but with less emphasis on certification weakness.

### D-008: Resource Requirements Framing
- **Opus-Architect**: Focuses on external dependencies (API stability checks) and new module creation with import graphs
- **Haiku-Analyzer**: Frames resources as team roles (primary engineer, QA, analyzer/reviewer) plus technical dependencies
- **Impact**: Opus is more useful for a solo developer (concrete module list, import chains). Haiku is more useful for team planning (role allocation, capability needs).

### D-009: Open Question Resolution Strategy
- **Opus-Architect**: 7 open questions with recommended defaults in a decision table
- **Haiku-Analyzer**: References same questions but treats them as Phase 0 blocking items requiring resolution before code starts
- **Impact**: Opus provides defaults to unblock development immediately. Haiku requires explicit resolution first. Opus's approach is faster; Haiku's is safer for ambiguous areas like SIGINT handling.

### D-010: Validation Layer Taxonomy
- **Opus-Architect**: Two layers — unit tests per phase, integration tests in P6
- **Haiku-Analyzer**: Five explicit layers — unit, integration, contract, performance, failure-path
- **Impact**: Haiku's taxonomy is more structured and actionable, explicitly separating contract tests (gate outputs, state schema) and failure-path tests (timeout, retry, interruption) as first-class categories.

### D-011: Critical Path Analysis
- **Opus-Architect**: Explicit critical path stated: P1 → P3 → P4 → P6 (13–18 days), with parallel opportunities documented
- **Haiku-Analyzer**: Sequential milestone sequence (M0–M6) without explicit critical path or parallelization analysis
- **Impact**: Opus provides better scheduling guidance for project management. Haiku's linear sequence implies less opportunity for overlap.

### D-012: Implementation Sequence Within Phase 3
- **Opus-Architect**: Specifies 8-step internal implementation order within P3 (prompt builder → grouping → snapshots → spawning → coordination → handlers → emitter → registration)
- **Haiku-Analyzer**: Lists 10 key actions without explicit internal ordering
- **Impact**: Opus provides a concrete build sequence for the highest-risk phase, reducing implementation ambiguity. Haiku leaves ordering to the implementer.

---

## 3. Areas Where One Variant Is Clearly Stronger

### Opus-Architect Strengths
- **Critical path analysis** with explicit parallel opportunities and overlap windows
- **Module-level architecture**: concrete file names, import dependency graphs, new module creation table
- **Internal phase sequencing** (especially P3's 8-step build order)
- **Token/cost estimates** for agent prompts (6–12K remediation, 2–3K certification)
- **Dependency status checks**: actionable verification steps before work begins

### Haiku-Analyzer Strengths
- **Phase 0 discovery**: Explicit ambiguity resolution before committing to implementation
- **Risk analysis depth**: More granular risk categorization with stronger emphasis on stale resume and false certification
- **Validation taxonomy**: Five-layer test strategy (unit, integration, contract, performance, failure-path) vs two-layer
- **Tasklist-before-orchestration sequencing**: More architecturally sound — plan then execute
- **Final recommendations section**: Actionable implementation guidance ("do not start with agent orchestration", "treat rollback as a release gate")
- **Compressed timeline**: More realistic for a focused engineering effort if assumptions hold

---

## 4. Areas Requiring Debate to Resolve

1. **Timeline calibration**: 15–20 days vs 7–9 days is a significant gap. Needs clarification on whether estimates are elapsed time, focused engineering hours, or include review/iteration cycles.

2. **Tasklist generation timing (D-004/D-005)**: Should the remediation tasklist be a pre-execution plan (Haiku) or a post-execution output (Opus)? The spec language around `REMEDIATE_GATE` and tasklist-as-audit-trail suggests Haiku's sequencing, but this needs explicit resolution.

3. **State schema timing (D-003)**: Front-loading state design (Opus P1) vs deferring to integration (Haiku P5). The trade-off is between early confidence in schema design vs avoiding premature schema decisions.

4. **Discovery phase value (D-001)**: Is a dedicated P0 worth 0.5–1 day, or is implicit discovery sufficient? Depends on team familiarity with the existing pipeline codebase.

5. **Open question resolution strategy (D-009)**: Provide defaults and proceed (Opus) vs block until resolved (Haiku). The right answer depends on risk tolerance and whether the defaults are truly safe.
