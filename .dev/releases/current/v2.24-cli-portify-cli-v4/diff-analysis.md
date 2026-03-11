

---
total_diff_points: 12
shared_assumptions_count: 18
---

# Diff Analysis: Opus-Architect vs Haiku-Analyzer Roadmaps

## 1. Shared Assumptions and Agreements

Both variants agree on these 18 foundational points:

1. **7-step pipeline** with mixed pure-programmatic and Claude-assisted steps
2. **13 Python modules** under `src/superclaude/cli/cli_portify/`
3. **Synchronous-only execution** — no async/await
4. **Zero modifications** to `pipeline/` and `sprint/` base modules
5. **Runner-authored truth** — Python determines status, not Claude self-reporting
6. **Mandatory reuse** of `/sc:brainstorm` and `/sc:spec-panel` skills
7. **Gate signature** as `tuple[bool, str]`
8. **Same FR coverage** (FR-001 through FR-007)
9. **Same external dependencies** (Click, Rich, PyYAML, `claude` CLI)
10. **Same internal dependencies** (pipeline.models, pipeline.gates, pipeline.process, sprint.models, sprint.process)
11. **Convergence terminal states**: CONVERGED, ESCALATED, BUDGET_EXHAUSTED, TIMEOUT
12. **Quality score formula**: mean(clarity, completeness, testability, consistency) with <0.01 tolerance
13. **Downstream readiness boundary**: 7.0 → true, 6.9 → false
14. **`@path` references** over inline artifact embedding
15. **Pre-flight checks** for skills and `claude` binary
16. **`--add-dir`** for subprocess file scope
17. **17 unit tests + 5 integration tests** target
18. **Additive-only spec modifications** during panel review

---

## 2. Divergence Points

### D-01: Phase Count and Structure

- **Opus-Architect**: 5 phases (P1–P5). Foundation and pure-programmatic steps merged into Phase 1.
- **Haiku-Analyzer**: 6 phases (P0–P5). Separates a **Phase 0** for architecture, contracts, and test scaffolding before any implementation.
- **Impact**: Haiku's Phase 0 frontloads contract definition and test planning, reducing downstream drift risk. Opus starts producing code sooner but may discover contract issues mid-implementation.

### D-02: Contract-First vs Implementation-First Sequencing

- **Opus-Architect**: Defines domain models and contracts as tasks within Phase 1 alongside implementation of Steps 1–2.
- **Haiku-Analyzer**: Insists contracts, gate interfaces, and test skeletons must be **approved before any implementation** begins. Explicitly warns: "If contracts are deferred, downstream steps will drift."
- **Impact**: Haiku's approach is more defensive and reduces rework. Opus's approach is faster to first output but carries integration risk.

### D-03: Monitoring Signal Vocabulary Timing

- **Opus-Architect**: Defers signal vocabulary definition to Phase 5 (Open Question GAP-008), resolving it during TUI monitor implementation.
- **Haiku-Analyzer**: Flags this as a Phase 0 concern, warning that "undefined monitoring/event vocabulary will become a late-stage blocker for diagnostics and resume logic."
- **Impact**: Haiku is correct that signal vocabulary affects resume state serialization and diagnostic output, both of which are implemented in earlier phases. Late definition risks rework.

### D-04: Resume Semantics Specification Depth

- **Opus-Architect**: Addresses resume in Phase 5 with a clear recommendation (re-run failed step entirely, don't trust partial artifacts). Mentions context injection from `focus-findings.md`.
- **Haiku-Analyzer**: Calls resume semantics "currently under-specified" and elevates them to a first-class concern. Recommends defining idempotency rules per step and treating failure contracts as core functionality, not cleanup.
- **Impact**: Both reach the same conclusion (re-run failed steps), but Haiku pushes for earlier specification. Haiku's framing as "first-class feature" is more aligned with the spec's emphasis on resumability.

### D-05: Timeline Estimates

- **Opus-Architect**: 17–22 working days (3–4 weeks) across 5 phases.
- **Haiku-Analyzer**: 13–18 working days across 6 phases (Phase 0 adds 1–2 days but Phase 1 is shorter at 2–3 days vs Opus's 3–4 days).
- **Impact**: Haiku's faster estimate likely reflects the smaller Phase 1 scope (pure-programmatic only, contracts already done in P0). The difference is modest (≈3–4 days). Haiku's lower bound (13 days) may be optimistic given convergence loop complexity.

### D-06: Risk Inventory Depth and Framing

- **Opus-Architect**: 9 enumerated risks in a table with severity/likelihood ratings. Includes one additional risk noted outside the table (template path stability).
- **Haiku-Analyzer**: Categorizes risks into High (4), Medium (4), and Low (1) priority tiers with more narrative mitigation detail. Adds explicit risk for "architectural drift from synchronous-only design" as a standalone high-priority item.
- **Impact**: Haiku's tiered risk framing is more actionable for prioritization. Opus's table format is more scannable. Haiku explicitly calls out architectural drift as a continuous risk, which Opus handles only via grep verification in Phase 5.

### D-07: Test Strategy Granularity

- **Opus-Architect**: Lists test counts per phase (6 + 5 + 3 + 4 = 18 unit, 5 integration). Specifies what each test covers but doesn't define a test execution sequence.
- **Haiku-Analyzer**: Defines a **recommended validation sequence** (contracts/gates → pure-programmatic → structural → convergence → end-to-end) and includes additional test scenarios (malformed panel output, empty workflow structures, name normalization edge cases).
- **Impact**: Haiku's validation sequence is more methodical. The additional edge case coverage (malformed output, empty structures) addresses real failure modes that Opus doesn't explicitly test.

### D-08: Parallelization Opportunity Analysis

- **Opus-Architect**: Explicitly identifies within-phase parallelization opportunities (e.g., models/CLI/gates in P1, prompts/executor in P2, unit tests/TUI in P5).
- **Haiku-Analyzer**: Recommends "incremental vertical slices over broad parallel implementation" — explicitly discouraging parallelization in favor of sequential slice delivery.
- **Impact**: Fundamentally different development philosophies. Opus optimizes for calendar time; Haiku optimizes for integration correctness. For a team of 1–2 developers (likely given scope), Haiku's vertical slice approach reduces context-switching overhead.

### D-09: Milestone Checkpoint Strategy

- **Opus-Architect**: No explicit inter-phase checkpoints beyond phase exit criteria.
- **Haiku-Analyzer**: Defines 5 named checkpoints (A–E) with specific validation goals at each, plus explicit "Analyzer Concerns" sections per phase acting as review prompts.
- **Impact**: Haiku's checkpoints provide clearer go/no-go decision points. The per-phase "Analyzer Concerns" sections serve as built-in review checklists that Opus lacks.

### D-10: Convergence Loop Architecture Detail

- **Opus-Architect**: Specifies single subprocess per iteration running both focus and critique (addressing R-009/GAP-006 explicitly). Includes budget estimation pre-launch guard and convergence counter reset on resume.
- **Haiku-Analyzer**: Covers the same ground but adds explicit test cases for edge conditions: "converged first iteration", "converged later iteration", "timeout per iteration", "malformed panel output."
- **Impact**: Opus has deeper architectural specification (single subprocess rationale, budget guards). Haiku has deeper test specification. Both are needed; they complement rather than conflict.

### D-11: Failure Classification Scope

- **Opus-Architect**: Lists failure types in Phase 5 diagnostics task: gate failure, subprocess crash, budget exhaustion, timeout, user rejection.
- **Haiku-Analyzer**: Adds "malformed artifact" and "missing skills" as explicit failure categories. Recommends standardizing event types and payload schemas for each.
- **Impact**: Haiku's broader classification catches real failure modes (malformed artifacts from Claude output variance). The payload schema recommendation supports machine-readable diagnostics.

### D-12: Role/Resource Recommendations

- **Opus-Architect**: No explicit role recommendations. Implicitly assumes a single developer.
- **Haiku-Analyzer**: Recommends 3 roles (lead backend/CLI engineer, QA/validation engineer, documentation/release engineer) with effort area mapping.
- **Impact**: Haiku's role breakdown is useful for team planning but may be aspirational — the spec seems scoped for 1–2 developers. Opus's implicit single-developer assumption is more realistic.

---

## 3. Areas Where One Variant Is Clearly Stronger

### Opus-Architect Strengths

| Area | Why Stronger |
|------|-------------|
| **Dependency verification** | Explicit pre-implementation checklist (confirm exports, verify `--add-dir` capability, check template path, verify skills). Actionable and concrete. |
| **Success criteria validation table** | Maps each SC-* criterion to validation method and phase — directly traceable. |
| **CLI options specification** | Complete enumeration of all flags (`--workflow`, `--output-dir`, `--dry-run`, `--skip-review`, `--model`, `--max-convergence`, `--resume-from`) in Phase 1. |
| **Open questions resolution** | Provides specific recommended resolutions for all 10 open questions with rationale. Haiku mentions them but doesn't resolve them systematically. |
| **Convergence architecture** | More detailed on single-subprocess rationale, budget estimation, and TurnLedger integration. |

### Haiku-Analyzer Strengths

| Area | Why Stronger |
|------|-------------|
| **Risk prioritization** | Tiered (High/Medium/Low) with narrative context. More actionable for triage. |
| **Contract-first discipline** | Phase 0 ensures all interfaces are stable before implementation. Reduces costly rework. |
| **Test edge cases** | Identifies specific scenarios Opus omits: malformed output, empty structures, name normalization, skill unavailability fallback. |
| **Continuous constraint enforcement** | Treats sync-only and base-module immutability as ongoing concerns, not just final verification. |
| **Per-phase review prompts** | "Analyzer Concerns" sections function as built-in code review checklists per phase. |
| **Validation sequence** | Explicit ordering of test execution from contracts → unit → structural → convergence → E2E. |

---

## 4. Areas Requiring Debate to Resolve

### Debate 1: Phase 0 — Necessary or Overhead?

Haiku's Phase 0 adds 1–2 days for contract/architecture approval before code. Opus folds this into Phase 1. The question: does the project's complexity (convergence loops, multi-step resume, skill integration) justify a dedicated contract-definition phase, or can contracts be defined alongside initial implementation?

**Recommendation**: Favor Haiku's Phase 0 for this project. Convergence loop contracts and resume state contracts are sufficiently complex that discovering mismatches during Phase 4 would be costly.

### Debate 2: Vertical Slices vs Parallel Tasks

Opus identifies parallelization opportunities within phases. Haiku explicitly recommends against parallelization in favor of vertical slices. For a small team, which approach yields better outcomes?

**Recommendation**: Needs team size context. For 1 developer, Haiku's vertical slices are clearly better. For 2+, Opus's within-phase parallelization (e.g., models + gates in P1) is viable.

### Debate 3: Monitoring Signal Vocabulary Timing

Opus defers to Phase 5; Haiku demands Phase 0. When should the 5-event vocabulary (`STEP_START`, `STEP_COMPLETE`, `GATE_PASS`, `GATE_FAIL`, `CONVERGENCE_ITERATION`) be defined?

**Recommendation**: Favor Haiku. The vocabulary is small (5 events) and affects resume state serialization, which is implemented before Phase 5. Define in Phase 0, implement in Phase 5.

### Debate 4: Open Question Resolution Approach

Opus provides a consolidated resolution table for all open questions. Haiku identifies them as risks but doesn't resolve them systematically. Should open questions be resolved upfront (Opus) or incrementally per phase (Haiku)?

**Recommendation**: Favor Opus's consolidated approach. The open questions are interdependent (e.g., score rounding affects convergence predicate, model propagation affects all subprocess steps). Resolving them together prevents inconsistency.

### Debate 5: Failure Classification as Core vs Cleanup

Haiku insists failure contracts are "first-class features, not cleanup work." Opus places diagnostics and failure classification in Phase 5. When should failure paths be fully specified?

**Recommendation**: Compromise. Define failure contract schemas in Phase 0/1 (per Haiku), implement full classification and diagnostics in Phase 5 (per Opus). This ensures downstream phases can emit proper failure contracts without requiring the full diagnostic system.
