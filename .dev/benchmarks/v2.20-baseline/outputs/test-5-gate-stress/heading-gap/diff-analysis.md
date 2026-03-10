

---
total_diff_points: 12
shared_assumptions_count: 14
---

# Diff Analysis: Opus-Architect vs Haiku-Analyzer Roadmap Variants

## 1. Shared Assumptions and Agreements

1. **Complexity score**: Both assign 0.65
2. **Spec source**: Both reference `spec-roadmap-validate.md`
3. **Purely additive design**: No breaking changes to existing pipeline
4. **Unidirectional dependency**: `validate_*` depends on `pipeline/*`, never vice versa
5. **Three new files**: `validate_gates.py`, `validate_prompts.py`, `validate_executor.py`
6. **Three modified files**: `models.py`, `commands.py`, `executor.py`
7. **Infrastructure reuse**: Both mandate reusing `execute_pipeline`, `ClaudeProcess`, `GateCriteria`
8. **7 validation dimensions** with BLOCKING/WARNING severity classification
9. **Exit code 0** regardless of blocking findings (NFR-006/SC-007)
10. **Gate hierarchy**: REFLECT_GATE (STANDARD) < ADVERSARIAL_MERGE_GATE (STRICT)
11. **Same CLI flags**: `--agents`, `--model`, `--max-turns`, `--debug`, `--no-validate`
12. **Same success criteria** (SC-001 through SC-009)
13. **Validation outputs** written to `<output-dir>/validate/`
14. **`--resume` semantics**: Only validate after full pipeline success

## 2. Divergence Points

### D-01: Phase Count and Granularity
- **Opus-Architect**: 5 phases — combines prompts with foundation, merges verification and hardening
- **Haiku-Analyzer**: 6 phases — separates standalone execution from multi-agent, adds dedicated release hardening phase
- **Impact**: Haiku's separation of single-agent (Phase 2) from multi-agent (Phase 3) provides a clearer vertical slice for incremental delivery. Opus's tighter grouping is more efficient if executed by a single developer.

### D-02: Parallelization of Early Work
- **Opus-Architect**: Explicitly states Phase 1 (gates) and Phase 2 (prompts) can run in parallel, reducing wall time
- **Haiku-Analyzer**: Groups gates and prompts into a single Phase 1, treating them as sequential within the phase
- **Impact**: Opus's approach yields faster wall time (~6-9 hours estimated). Haiku's bundling reduces coordination overhead but extends the critical path.

### D-03: Timeline Units
- **Opus-Architect**: Estimates in hours (6-9 hours total wall time)
- **Haiku-Analyzer**: Estimates in days (4.5-7 days across 6 phases, "2-3 implementation iterations")
- **Impact**: Significant divergence. Opus treats this as a focused sprint; Haiku as a multi-day effort. The actual scope (3 new files, 3 modifications) better supports Opus's hours-based estimate for a single experienced developer.

### D-04: Standalone CLI Integration Timing
- **Opus-Architect**: CLI wiring deferred to Phase 4, after executor is complete
- **Haiku-Analyzer**: CLI subcommand added in Phase 2 alongside standalone execution
- **Impact**: Haiku enables earlier manual testing via CLI. Opus ensures the executor is fully tested before exposing it through CLI, reducing rework risk.

### D-05: State Persistence Recommendation
- **Opus-Architect**: Explicitly recommends recording validation status in `.roadmap-state.json` under a `validation` key (Open Question 4)
- **Haiku-Analyzer**: Explicitly recommends keeping validation state separate from roadmap execution state "unless future requirements demand tracking"
- **Impact**: Opus's approach enables `--resume` to skip re-validation; Haiku's is simpler but loses cross-session awareness. This is a genuine design disagreement requiring resolution.

### D-06: Interleave Ratio Formula
- **Opus-Architect**: Proposes concrete formula (`unique_phases_with_deliverables / total_phases`) and recommends resolving before Phase 2
- **Haiku-Analyzer**: Identifies it as an open question to triage in Phase 6
- **Impact**: Opus's early resolution prevents prompt instability. Haiku's deferral risks rework if the formula affects validation accuracy.

### D-07: Failure Semantics (Partial Multi-Agent)
- **Opus-Architect**: Recommends surfacing partial results — if agent A succeeds and B fails, produce degraded report from A's output
- **Haiku-Analyzer**: Identifies this as an open question deferred to Phase 6
- **Impact**: Opus provides a clear degraded-mode path. Haiku leaves this unresolved, creating implementation ambiguity in Phase 3.

### D-08: Resource/Team Model
- **Opus-Architect**: Implicitly assumes single developer, no role separation
- **Haiku-Analyzer**: Explicitly identifies 3 engineering roles (CLI/executor, validation logic, QA) plus 2 optional reviewers
- **Impact**: Haiku's role separation is more realistic for team-based delivery but over-scoped for this moderate-complexity feature.

### D-09: Risk Assessment Depth
- **Opus-Architect**: 6 risks with compact mitigation strategies
- **Haiku-Analyzer**: 7 risks organized by priority tier (High/Medium/Low) with more detailed mitigation plans
- **Impact**: Haiku's tiered approach provides better prioritization. Opus's is sufficient but less actionable for risk triage.

### D-10: Test Strategy Specificity
- **Opus-Architect**: References spec section 10 (7 unit + 4 integration tests) without detailing test scenarios
- **Haiku-Analyzer**: Enumerates specific test categories including known-defect detection tests (duplicate D-ID, missing milestone, untraced requirements) and negative tests for shallow outputs
- **Impact**: Haiku's test enumeration provides clearer implementation guidance for QA.

### D-11: Documentation Scope
- **Opus-Architect**: No explicit documentation deliverable
- **Haiku-Analyzer**: Phase 6 includes operational documentation (standalone use, multi-agent trade-offs, `--resume` semantics)
- **Impact**: Haiku addresses a real gap — user-facing documentation for the new command.

### D-12: Framing and Recommendation Style
- **Opus-Architect**: Framed as technical implementation plan with architecture-first perspective
- **Haiku-Analyzer**: Framed as risk-aware analysis with "contract-first integration" recommendation, emphasizing failure modes over features
- **Impact**: Haiku's emphasis on "false confidence, merge correctness, resume gating, and architectural drift" as primary failure modes provides better risk awareness.

## 3. Areas of Clear Strength

### Opus-Architect Strengths
- **Parallelization planning**: Explicit identification of Phase 1‖2 parallelism with wall-time savings
- **Concrete open-question resolution**: Provides actionable answers (interleave formula, state persistence, partial failure) rather than deferring
- **Realistic timeline**: Hours-based estimate matches the actual scope better
- **File modification table**: Clean mapping of files → change types → phases

### Haiku-Analyzer Strengths
- **Risk prioritization**: Tiered risk assessment (High/Medium/Low) with clearer triage guidance
- **Test specificity**: Enumerated test scenarios including negative and defect-injection tests
- **Vertical slice delivery**: Phase 2 delivers a testable standalone command before multi-agent complexity
- **Documentation awareness**: Includes operational docs as an explicit deliverable
- **Failure mode focus**: Final recommendation correctly identifies the real risks (merge correctness, false confidence) over feature delivery

## 4. Areas Requiring Debate

1. **State persistence** (D-05): Should validation status be recorded in `.roadmap-state.json`? Opus says yes for `--resume` support; Haiku says no for simplicity. This needs a decision based on whether `--resume` re-validation skipping is a real user need.

2. **Interleave ratio timing** (D-06): Resolve before prompts (Opus) or defer to hardening (Haiku)? Opus's position is stronger — undefined formulas in prompts produce inconsistent validation results.

3. **Partial failure handling** (D-07): Degraded report (Opus) vs unresolved (Haiku)? This must be decided before Phase 3 implementation begins regardless of which variant is chosen.

4. **Timeline realism** (D-03): 6-9 hours vs 4.5-7 days. The scope supports the hours estimate for a single developer familiar with the codebase. The days estimate may reflect a team-based delivery model with review cycles.
