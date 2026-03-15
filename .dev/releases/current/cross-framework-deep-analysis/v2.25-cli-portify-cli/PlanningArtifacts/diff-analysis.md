---
total_diff_points: 18
shared_assumptions_count: 14
---

## Shared Assumptions and Agreements

Both variants agree on all of the following:

1. **Scope**: 65 requirements (47 functional, 18 non-functional), complexity 0.92/enterprise, 8 domains, 14 success criteria
2. **Core architecture**: `src/superclaude/cli/cli_portify/` module registered in `src/superclaude/cli/main.py`
3. **Sequential-only pipeline** — no parallel step groups in execution
4. **12-gate enforcement** with STANDARD/STRICT tiers and `GateMode.BLOCKING`
5. **Convergence loop**: 3-iteration cap, CONVERGED/ESCALATED states, `downstream_ready = true` when `overall >= 7.0`
6. **Domain models extend pipeline framework base types** (`PipelineConfig`, `Step`, `StepResult`, etc.)
7. **Hard dependency**: `claude` CLI binary via `shutil.which("claude")`, exit 124 → TIMEOUT
8. **Turn budget ledger** with pre-launch check and halt behavior
9. **Return contract emission on all code paths** (success, failure, interrupt, dry-run)
10. **Resume flow**: approval YAML file, `--resume <step-id>` skips completed steps
11. **`portify-release-spec.md`** produced via 13-section template population + brainstorm enrichment + placeholder validation
12. **Panel review**: 4 experts (Fowler, Nygard, Whittaker, Crispin), severity routing (CRITICAL/MAJOR/MINOR)
13. **Observability stack**: `execution-log.jsonl`, `execution-log.md`, `OutputMonitor`, `PortifyTUI`
14. **UV-only execution** per project CLAUDE.md constraints

---

## Divergence Points

### 1. Phase count and granularity
- **Opus (architect)**: 6 phases (A–F), 15 milestones
- **Haiku (analyzer)**: 11 phases (0–10), 11 milestones
- **Impact**: Haiku's finer granularity provides more checkpoints and reduces risk of large phase failures. Opus's coarser phases are simpler to track but bundle more risk into each exit gate.

### 2. Architecture confirmation phase
- **Opus**: No dedicated pre-implementation confirmation phase; resolves open questions "before respective phases"
- **Haiku**: Explicit Phase 0 (0.5–1 day) to lock interface assumptions, resolve OQs, confirm base type imports before any coding
- **Impact**: Haiku's Phase 0 prevents rework on contract-critical areas. Opus risks discovering blocking OQs mid-implementation.

### 3. Observability timing
- **Opus**: Observability (monitor, logging, TUI) implemented in Phase B alongside executor core
- **Haiku**: Observability implemented in Phase 8, **but explicitly recommends moving it earlier** (before Phase 4 Claude steps) in "Recommended execution order adjustments"
- **Impact**: Haiku's explicit recommendation is operationally sounder — diagnostics are needed before long-running Claude steps fail. Opus's phase ordering achieves the same end but doesn't call this out as a risk-reduction strategy.

### 4. Timeline estimates
- **Opus**: No explicit day estimates per phase (uses Large/Medium descriptors)
- **Haiku**: Explicit day ranges per phase; total **15.0–22.5 working days**
- **Impact**: Haiku provides actionable planning data. Opus's qualitative estimates are insufficient for project management.

### 5. Open question handling
- **Opus**: Lists 14 OQs (OQ-001 through OQ-014) organized by phase dependency, embedded in Section 4
- **Haiku**: Treats 5 key OQs as blocking for Phase 0 with an explicit "do not begin implementation" recommendation; deprioritizes the rest
- **Impact**: Haiku's approach is more decisive and reduces ambiguity about what must be resolved vs. what can be deferred. Opus's list is more complete but doesn't distinguish blocking from non-blocking.

### 6. Gate implementation scope detail
- **Opus (Milestone B1)**: Explicitly enumerates specific gate checks: `EXIT_RECOMMENDATION` detection, `has_zero_placeholders`, step-count consistency, return type pattern check, G-002/G-003/G-005–G-008/G-010 marker mapping
- **Haiku (Phase 3)**: Lists gate categories but without per-gate specificity for which semantic check applies to which gate ID
- **Impact**: Opus provides more complete implementation guidance for the gate system; Haiku would require referencing the spec for gate-to-check mappings.

### 7. Module generation order constraint
- **Opus**: Mentioned briefly in Milestone E3 as "document and enforce," referencing NFR-006 and AC-012
- **Haiku**: Explicitly enumerates the full 13-module generation order in Phase 9 (models → gates → prompts → config → inventory → monitor → process → executor → tui → logging_ → diagnostics → commands → `__init__`)
- **Impact**: Haiku is more actionable for the implementer. Opus defers the enumeration to the spec.

### 8. Resource requirements / team structure
- **Opus**: No team structure recommendations
- **Haiku**: Explicitly recommends 3 roles (primary engineer, analyzer/reviewer, QA support) with effort split (40/25/20/15%)
- **Impact**: Haiku is more useful for project planning and staffing decisions.

### 9. Validation organization
- **Opus**: 14-row table mapping each SC to phase, validation method, and specific test type
- **Haiku**: 3-category structure (structural / behavioral / operational) + recommended sequence of 9 test stages
- **Impact**: Opus's table is better for traceability to SCs. Haiku's sequential test ordering is better for execution planning. Both are valuable; neither is redundant.

### 10. Approval file validation
- **Opus (R-008)**: Notes string match approach and "consider adding YAML parse validation" as an afterthought
- **Haiku**: Explicitly recommends YAML parse + schema validation over raw string matching as a firm recommendation (#4 in Final Recommendations)
- **Impact**: Haiku takes a stronger, safer position. Opus hedges.

### 11. Milestone grouping for external communication
- **Opus**: Phases map 1:1 to milestones; no higher-level grouping
- **Haiku**: Introduces 3 super-milestones (A: Foundations, B: Pipeline generation, C: Quality loop) with cumulative time estimates
- **Impact**: Haiku's grouping is more useful for stakeholder reporting and go/no-go decisions.

### 12. Risk table completeness
- **Opus**: 4 critical risks + 5 moderate risks in tables; includes unlisted "Framework Base Type Stability" architectural risk as a separate callout
- **Haiku**: 12 numbered risks (4 high, 6 medium, 2 low) with structured mitigation + explicit "Roadmap response" mapping to phases
- **Impact**: Haiku's "Roadmap response" field closes the loop between risk identification and mitigation implementation. Opus's architectural risk callout (base type stability) is unique and not present in Haiku.

### 13. `--debug` flag specification
- **Opus**: Acknowledged as OQ-011 ("define `--debug` flag behavior")
- **Haiku**: Treats debug semantics as blocking for Phase 0 — must be resolved before implementation
- **Impact**: Haiku correctly recognizes that debug mode can affect subprocess behavior and logging paths, making it contract-critical.

### 14. Prompt splitting implementation location
- **Opus (Milestone E2)**: Located in CLI entry point (`commands.py`)
- **Haiku (Phase 0)**: Flags this as an architectural question — "confirm whether prompt splitting threshold implementation should be in executor or prompt builder"
- **Impact**: Haiku surfaces an architectural ambiguity that Opus resolves by assumption without justification. Haiku's position is more cautious.

### 15. Dry-run phase boundaries
- **Opus**: "Limit to PREREQUISITES, ANALYSIS, USER_REVIEW, SPECIFICATION phase types" (FR-037, SC-012)
- **Haiku**: "`--dry-run` stops after Phase 2 boundary" (more implementation-oriented framing)
- **Impact**: Opus's formulation ties directly to spec enumeration (FR-037), making it more traceable. Haiku's formulation is more intuitive but less precise.

### 16. `stall_action: kill` implementation detail
- **Opus**: References `stall_action: kill` with SIGTERM→SIGKILL escalation via `OutputMonitor.growth_rate_bps` as a note in R-001
- **Haiku**: Treats SIGTERM grace period → SIGKILL as a firm kill policy (OQ-002 resolution), explicitly preferred over immediate SIGKILL
- **Impact**: Haiku takes a position on OQ-002; Opus leaves it open. Both agree on monitoring approach.

### 17. `decisions.yaml` schema
- **Opus**: Flagged as OQ-012 to document, no resolution
- **Haiku**: Not explicitly addressed
- **Impact**: Neither variant resolves this; both leave it to spec reference.

### 18. Workdir cleanup policy
- **Opus**: OQ-014 flagged, no resolution
- **Haiku**: Listed under low-priority risks (R-12) with "document cleanup expectations" as mitigation
- **Impact**: Haiku at least assigns it a risk level and mitigation category, even if resolution is deferred.

---

## Areas Where One Variant Is Clearly Stronger

### Haiku (analyzer) is stronger in:
- **Project planning**: Explicit day estimates, team structure, effort split, super-milestone grouping
- **Risk-to-implementation traceability**: "Roadmap response" field connects each risk to the phase that addresses it
- **Pre-implementation discipline**: Phase 0 prevents costly mid-implementation OQ discoveries
- **Observability timing**: Correctly identifies that diagnostics must precede long-running Claude steps
- **Approval file safety**: Takes a firm position on YAML parse vs. string match
- **Module generation order**: Explicit enumeration vs. a cross-reference to the spec

### Opus (architect) is stronger in:
- **Gate system detail**: Per-gate semantic check mapping (which check applies to which gate ID)
- **SC-to-validation traceability**: Table format with exact test type per success criterion
- **Architectural risk identification**: "Framework Base Type Stability" risk is unique and important — a base type API change breaks all domain models
- **Spec reference fidelity**: Consistently cites FR/NFR/AC/SC numbers, making cross-referencing easier
- **Dry-run precision**: FR-037 citation ties the boundary to the spec unambiguously

---

## Areas Requiring Debate to Resolve

1. **Phase 0 (architecture lock) — include or omit?** Haiku treats it as mandatory; Opus folds OQ resolution into each phase. If any OQ is contract-breaking, Opus's approach risks wasted implementation effort. Recommend: adopt Haiku's Phase 0 with Opus's OQ enumeration as its input.

2. **Observability phase placement**: Both agree it should be early, but the phase ordering in Opus (B, early) vs. Haiku's recommendation (before Phase 4, mid-sequence) needs an explicit decision. Haiku's recommendation is operationally sound but creates an awkward phase dependency if Phase 8 deliverables are needed in Phase 4.

3. **Validation strategy — table vs. sequence**: These are complementary, not competing. The merged approach (Opus's SC-to-method table + Haiku's 9-stage test sequence) is superior to either alone. Debate needed only on whether to maintain both or consolidate.

4. **Prompt splitting location**: Haiku flags this as an architectural question; Opus assigns it to the CLI layer. This needs explicit resolution before Phase C/Phase 4 implementation begins, as it affects both `prompts.py` and `commands.py` design.

5. **OQ priority classification**: Opus lists all 14 OQs without priority; Haiku identifies 5 as blocking. The 5 Haiku marks as blocking (TurnLedger semantics, phase_contracts schema, hash algorithm, failure type enum, debug behavior) should be validated against the spec — if any of the remaining 9 also affect contracts, they need to be elevated.
