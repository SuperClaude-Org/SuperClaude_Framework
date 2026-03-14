

---
total_diff_points: 12
shared_assumptions_count: 14
---

# Diff Analysis: Opus Architect vs Haiku Architect Roadmaps

## 1. Shared Assumptions and Agreements

1. **Spec fidelity**: Both derive from the same `portify-release-spec.md` and agree on complexity score (0.65) and persona (architect)
2. **Core deliverable**: `resolution.py` as the central new module handling 6 input forms
3. **Backward compatibility as primary constraint**: Both treat preserving existing skill-directory workflows as the dominant risk
4. **No modifications to `pipeline/` or `sprint/`**: Hard boundary respected by both
5. **No async code**: Synchronous-only constraint acknowledged identically
6. **Model-first sequencing**: Both agree models/dataclasses must be built before resolution logic
7. **Same dataclass set**: `ResolvedTarget`, `CommandEntry`, `SkillEntry`, `AgentEntry`, `ComponentTree` appear in both
8. **Same error code set**: `ERR_TARGET_NOT_FOUND`, `ERR_AMBIGUOUS_TARGET`, `ERR_BROKEN_ACTIVATION`, `WARN_MISSING_AGENTS`
9. **Command-first ambiguity policy**: Both encode bare-name command precedence over skill
10. **6 agent regex patterns**: Identical extraction pattern list (backtick, YAML arrays, spawn/delegate/invoke, uses, model-parenthetical, agents/ paths)
11. **Directory cap at 10**: Both use `os.path.commonpath()` consolidation with resolution log
12. **`--include-agent` as escape hatch**: Same deduplication and override semantics
13. **Missing agents as warnings, not errors**: Non-fatal pipeline continuation
14. **Deferred items alignment**: Recursive agent resolution, manifest load, exclude-component all deferred to v2.25+

## 2. Divergence Points

### D-1: Phase Count and Granularity

- **Opus**: 3 phases with nested milestones (1.1, 1.2, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3)
- **Haiku**: 8 phases (0–7), each a flat unit with its own milestone

**Impact**: Opus's coarser phases enable more parallel work within phases but give less granular progress tracking. Haiku's finer phases provide clearer checkpoints but may introduce overhead in phase transitions.

### D-2: Phase 0 — Explicit Guardrails Phase

- **Opus**: No explicit Phase 0; jumps directly into model work
- **Haiku**: Dedicates Phase 0 (0.25 units) to establishing guardrails, change maps, compatibility checklists, and test matrix outlines before any code

**Impact**: Haiku's approach reduces risk of scope drift and provides a contractual baseline. Opus assumes this is implicit or done pre-roadmap. For a compatibility-sensitive release, Haiku's explicit guardrail phase is arguably safer.

### D-3: Parallelization Strategy

- **Opus**: Explicitly marks milestones 2.1 and 2.2 as parallelizable; also notes Phase 1 milestones (models + resolution) as independent/parallel
- **Haiku**: Notes discovery/process can run in parallel (Phase 3+4) after model contracts stabilize, but phases are presented more sequentially

**Impact**: Opus provides more actionable parallel execution guidance, which could reduce wall-clock time by ~20-30%. Haiku's sequential presentation is more conservative but clearer for a single implementer.

### D-4: Time Estimation Units

- **Opus**: Uses absolute hours (19-28 hours across 3 phases)
- **Haiku**: Uses relative "phase units" (5.25 total) with session-based grouping

**Impact**: Opus's hour estimates are more actionable for project planning. Haiku's abstract units avoid false precision but require calibration to be useful. Neither approach is clearly superior without knowing team velocity.

### D-5: Resolution Module Sizing

- **Opus**: Explicitly sizes `resolution.py` at ~350-450 lines
- **Haiku**: No line count estimate

**Impact**: Opus's estimate helps with scoping reviews and detecting scope creep during implementation. Haiku's omission avoids anchoring but loses a useful planning signal.

### D-6: Validation/Config Placement

- **Opus**: Validation extension (`validate_config.py`) is in Phase 3 alongside artifact enrichment and final tests
- **Haiku**: Validation is its own Phase 6, after CLI/config (Phase 5), giving it dedicated focus

**Impact**: Haiku's separation gives validation logic dedicated attention and prevents it from being rushed as part of "final cleanup." Opus bundles it with other Phase 3 work, which could lead to validation being deprioritized if time runs short.

### D-7: Existing Test Suite Execution Timing

- **Opus**: Architectural recommendation (#4) says "run existing tests at every milestone, not just Phase 3" but the formal validation gate is Phase 3.3
- **Haiku**: Phase 0 establishes regression as a continuous concern; Phase 7 is the formal gate but backward-compat tests are referenced throughout

**Impact**: Both advocate continuous testing but Opus is more explicit about making it a recommendation. Haiku embeds it structurally. Opus's disconnect between recommendation and formal gate is a minor inconsistency.

### D-8: Dependency Graph Visualization

- **Opus**: Provides an ASCII dependency graph showing module relationships and parallelization opportunities
- **Haiku**: Lists dependencies textually in a numbered plan without visual graph

**Impact**: Opus's visual is immediately actionable for implementation planning. Haiku's text description requires mental model construction.

### D-9: Risk Table Structure

- **Opus**: 6 risks in a table with severity, probability, mitigation, and phase mapping
- **Haiku**: 7 risks organized by priority tier (high/medium/low) with narrative mitigation

**Impact**: Opus's table is more scannable. Haiku's tiered narrative provides more context for each risk. Haiku adds "CLI contract drift confuses current users" as a distinct medium-priority risk that Opus doesn't separate out.

### D-10: Success Criteria Presentation

- **Opus**: 12 numbered SC items with explicit test methods and phase assignments in a table
- **Haiku**: 12 functional acceptance criteria plus 4 validation streams (unit/integration/regression/NFR) with a release gate checklist

**Impact**: Opus ties criteria to specific test implementations. Haiku organizes by validation methodology. Opus is more traceable; Haiku is more systematic about coverage categories.

### D-11: Consolidation Fallback Strategy

- **Opus**: `commonpath()` consolidation only
- **Haiku**: `commonpath()` first, then "if still over cap, select top 10 by component count" as explicit fallback

**Impact**: Haiku's two-tier fallback is more robust for edge cases where `commonpath()` doesn't sufficiently reduce directory count. This is a concrete implementation advantage.

### D-12: Architectural Recommendations Section

- **Opus**: 5 explicit architectural recommendations as a dedicated section (pure resolution, boundary conversion, regex constants, continuous testing, resolution logging)
- **Haiku**: Single "Architect recommendation" paragraph focused on compatibility-first delivery philosophy, with architectural guidance embedded in per-phase "Architect focus" callouts

**Impact**: Opus's centralized recommendations are easier to reference during implementation. Haiku's distributed approach provides guidance at the point of relevance. Both have merit for different consumption patterns.

## 3. Areas Where One Variant Is Clearly Stronger

### Opus is stronger in:
- **Parallel execution planning**: Explicit marking of parallelizable milestones with dependency rationale
- **Concrete sizing**: Hour estimates, line count for `resolution.py`, test count (~37)
- **Dependency visualization**: ASCII graph showing module relationships
- **Centralized architectural guidance**: Dedicated recommendations section with actionable items
- **External dependency table**: Explicit risk assessment per external dependency

### Haiku is stronger in:
- **Phase 0 guardrails**: Explicit pre-implementation contract establishment reduces compatibility risk
- **Consolidation fallback**: Two-tier strategy (commonpath → top-10-by-count) handles more edge cases
- **Validation stream organization**: Four named streams (unit/integration/regression/NFR) provide clearer coverage mapping
- **Per-phase architectural focus**: "Architect focus" callouts explain *why* each phase matters architecturally
- **CLI risk separation**: Explicitly identifies CLI contract drift as a distinct medium-priority risk
- **Release gate formulation**: 5-point release gate checklist is more actionable than Opus's "all 12 SC pass"

## 4. Areas Requiring Debate to Resolve

1. **Phase granularity**: 3 phases with sub-milestones (Opus) vs 8 discrete phases (Haiku). Depends on team size and whether progress tracking or parallel execution is prioritized.

2. **Phase 0 necessity**: Is an explicit guardrail phase worth 0.25 units, or is it overhead for a well-understood spec? If the team has already internalized the constraints, Opus's direct start is faster. If multiple implementers are involved, Haiku's contract is safer.

3. **Time estimation approach**: Hours (Opus: 19-28h) vs abstract phase units (Haiku: 5.25). Need to decide which provides better planning value for this team's workflow.

4. **Where to place validation logic**: Bundled with final phase (Opus) vs dedicated phase (Haiku). If validation is truly additive (just new checks), bundling is fine. If it reveals design issues, a dedicated phase prevents late rework.

5. **Consolidation strategy completeness**: Is `commonpath()` alone sufficient (Opus), or should the component-count fallback (Haiku) be specified upfront? Answerable by examining real-world directory distributions in existing skills.
