

---
convergence_score: 0.72
rounds_completed: 3
---

# Adversarial Debate: Opus Architect (Variant A) vs Haiku Analyzer (Variant B)

---

## Round 1: Initial Positions on Divergence Points

### Variant A (Opus Architect)

**On Phase Granularity (D-01):** Five phases is the correct granularity. Each phase maps to a coherent delivery unit with clear entry/exit criteria. Eight phases creates coordination overhead — more handoffs, more contracts to validate, more milestone ceremonies — without proportional safety gain. The bundling of contract infrastructure with Phase 0/1 in our Phase 2 is intentional: contracts are tested *by using them*, not in isolation.

**On Timeline Units (D-02):** Sessions are the honest unit. This is a Claude Code execution context. A "working day" implies 8 hours of continuous human effort, which misrepresents how this work actually proceeds. Sessions accurately reflect the execution model: load context, execute a coherent chunk, checkpoint. Ambiguity in session length is a feature — it accommodates variable complexity per session.

**On Contract Framework Timing (D-03):** Building contracts alongside their first consumers (Phase 0/1) is faster and produces better-tested contracts. Contract schemas designed in isolation risk being theoretically clean but practically misaligned with the data phases actually produce. We build the road by walking it.

**On OQ Resolution (D-04):** Resolve all 10 OQs in one batch before Phase 2. Deferring OQ resolution creates a moving target. Progressive resolution sounds flexible but means Phase 2 implementation begins with unresolved ambiguities — exactly the condition that causes rework. OQ-007 (approval gate mechanism) is blocking because it affects the contract infrastructure itself.

**On Legacy Removal (D-05):** Defer removal to Phase 5, after all validation passes. This is non-negotiable. The old directory is a rollback path. Removing it early creates an irreversible decision point before the replacement is proven.

**On Concrete Decisions (D-10, D-13):** We provide specific resolutions for `--dry-run`, `--skip-integration`, TurnLedger, and output defaults. A roadmap that defers all decisions to "clarify later" isn't a roadmap — it's a wish list. Concrete decisions can be wrong, but they're debuggable. Ambiguity is not.

### Variant B (Haiku Analyzer)

**On Phase Granularity (D-01):** Eight phases with single-responsibility boundaries is the safer structure for an enterprise-complexity (0.92) project. Opus bundles contract infrastructure, Phase 0, and Phase 1 into a single "Phase 2" — three fundamentally different concerns. When one fails, it's unclear which part needs rework. Finer phases produce clearer failure signals, more natural parallelization points, and more honest progress tracking.

**On Timeline Units (D-02):** Days are the only actionable planning unit. "14-19 sessions" is meaningless for project planning — sessions have no defined duration, no calendar anchor, no way to set deadlines or track velocity. Our 26-41 day range with optimistic/likely/conservative estimates gives stakeholders real information. The conservative estimate (41 days) reflects enterprise-complexity realism; Opus's 14-19 sessions could mean anything from 3 weeks to 3 months.

**On Contract Framework Timing (D-03):** Contracts must be proven before any phase depends on them. If you discover a contract design flaw while simultaneously implementing Phase 0 and Phase 1, you're debugging three things at once. Our Phase B isolates the contract framework, tests it with synthetic failures, and proves resume semantics work — all before Phase 0 generates its first real contract.

**On OQ Resolution (D-04):** Progressive resolution is more realistic. Not all OQs are equally urgent. OQ-009 (test placement) doesn't block anything until Phase G. Forcing all 10 resolutions into one batch creates artificial urgency and may produce hasty decisions on non-blocking items. We flag OQ-008 and OQ-009 as blocking (Opus doesn't) because output defaults and test placement affect integration design.

**On Legacy Removal (D-05):** We acknowledge Opus's point here — our phrasing in Phase A ("remove deprecated legacy directory after migration validation") was imprecise. However, "migration validation" means validating the structural split, not validating the entire pipeline. The old directory serves no purpose after the protocol structure is proven correct.

**On Role Definitions (D-06):** Explicit roles clarify responsibility even in a single-agent context. When Claude Code executes different phases, it activates different personas — the Analyzer Lead for workflow decomposition, the CLI Engineer for code generation, the QA Engineer for fixture testing. Roles make this persona switching explicit rather than implicit.

**On Negative Testing (D-09, D-11):** Our broader negative-path fixture suite (stale ref, API drift, name collision, non-portified collision) treats failure scenarios as first-class test cases, not afterthoughts distributed across milestones. Our determinism enumeration (`source_step_registry`, `step_mapping`, `module_plan`) is precise and testable — Opus's "diff output" is vague.

---

## Round 2: Rebuttals

### Variant A Rebuts Variant B

**On 8 phases:** Variant B claims finer granularity produces "clearer failure signals," but at 0.92 complexity, the overhead of 8 phase boundaries, 8 contracts, 8 entry/exit validation cycles is substantial. Each boundary is a potential failure point itself. Our 5-phase model has 14 milestones within it — that's plenty of granularity for failure isolation without the coordination tax of 8 top-level phases. Phase B (contracts in isolation) is the specific concern: you cannot validate contracts meaningfully without real data flowing through them.

**On day-based estimates:** Variant B's "26-41 working days" range has a 58% spread (41/26). That's not precision — it's uncertainty masquerading as planning rigor. Our "14-19 sessions" has a 36% spread and is honest about the execution model. If stakeholders need calendar dates, they can multiply by their expected hours-per-session. We refuse to provide false precision.

**On progressive OQ resolution:** Variant B says OQ-009 (test placement) doesn't block until Phase G. But design decisions in Phase E (generation specification) already need to know where tests go — the structural test file template depends on this. Deferring creates implicit assumptions that become explicit bugs. Batch resolution forces all decisions to be made coherently.

**On role definitions:** In a single-agent Claude Code context, roles are pure overhead. Claude Code doesn't need role definitions to activate the right persona — it does this automatically via keyword and context detection (per PERSONAS.md). Adding 5 named roles to a roadmap consumed by a single agent adds noise without signal.

**On legacy removal:** Variant B's "migration validation" is underspecified. When exactly is the structural split "proven correct"? After Phase A? After Phase C? The only safe answer is "after the entire pipeline is validated end-to-end" — which is our Phase 5.

### Variant B Rebuts Variant A

**On contract isolation:** Opus claims contracts should be "tested by using them." This is the classic integration-testing fallacy applied to infrastructure. When Phase 0 fails, is it a Phase 0 bug or a contract infrastructure bug? Opus's bundled Phase 2 makes this ambiguous. Our Phase B proves contract mechanics work (validation, resume, failure emission) before any real phase data exists. This is the same reason you test database migrations before running production queries.

**On batch OQ resolution:** Opus resolves all 10 OQs in Milestone 1.3, including OQ-005 (`batch_dynamic: false` always) and OQ-006 (verify `analysis-protocol.md` exists). These are trivially resolvable and don't need a batch process. Forcing them into the same milestone as genuinely blocking OQs (002, 003, 004) conflates triage urgency. More critically, Opus flags OQ-007 (approval gate mechanism) as blocking but not OQ-008 (default output) — yet the output default affects every phase's contract emission path.

**On session-based estimates:** Opus's defense of sessions ("ambiguity in session length is a feature") is an admission that the estimates are not actionable. A feature is something that helps users. Ambiguous duration helps no one making resourcing or scheduling decisions. Our range (26-41 days) gives a concrete planning envelope; Opus's range (14-19 sessions) gives an abstract one.

**On negative testing scope:** Opus distributes failure scenarios across Milestones 5.1, 5.2, and 5.3 without a unified negative-testing strategy. Our Phase H treats negative-path validation as a coherent test domain with its own fixtures. When a new failure mode is discovered, our model has a clear home for it. Opus's distributed model requires figuring out which milestone to retrofit.

**On concrete decisions:** Opus claims decisions like `--dry-run = Phases 0-2 only` are "debuggable." But a roadmap making implementation decisions without stakeholder input is a roadmap making assumptions. We defer these to Phase A resolution specifically so they can be debated with evidence from the codebase inspection. A premature decision in a roadmap is harder to reverse than a deferred one.

**On schema versioning (D-12):** Opus doesn't address contract schema versioning at all. If a contract schema needs to change during development (likely at 0.92 complexity), there's no policy for backward compatibility. Our explicit recommendation to define versioning policy prevents a class of problems Opus hasn't considered.

---

## Round 3: Concessions and Remaining Disagreements

### Variant A Concessions

1. **Schema versioning (D-12):** Variant B is correct that contract schema versioning should be addressed. We should add a versioning policy to Milestone 2.1 (contract infrastructure). This is a genuine gap in our roadmap.

2. **Determinism specificity (D-11):** Variant B's enumeration of which artifacts must be deterministic (`source_step_registry`, `step_mapping`, `module_plan`) is more testable than our "diff output." We should adopt this specificity in Milestone 5.1.

3. **Negative fixture breadth (D-09):** The stale-ref, API-drift, and collision-specific fixtures are valuable additions to the golden fixture suite. We would add these to Milestone 5.1 rather than creating a separate phase, but the test cases themselves are well-chosen.

4. **OQ-008 blocking status (D-04):** On reflection, the default output path does affect contract emission and should be classified as blocking for Phase 2. We concede this classification.

### Variant A Remaining Disagreements

1. **Phase granularity:** 5 phases with internal milestones remains superior to 8 top-level phases. The overhead is real and the safety gain is marginal given our milestone-level granularity.

2. **Contract isolation:** Building and testing contracts alongside their first real consumers produces better contracts than isolated testing with synthetic data.

3. **Timeline units:** Sessions remain the honest unit for single-agent Claude Code execution. Days are false precision.

4. **Legacy removal timing:** Deferred to Phase 5. Non-negotiable.

5. **Role definitions:** Noise in a single-agent context.

### Variant B Concessions

1. **Legacy removal timing (D-05):** Opus is correct that deferring removal to after full validation is safer. Our Phase A phrasing was imprecise and should be amended to: "Deprecate legacy directory in Phase A; remove in Phase H after all validation passes."

2. **Role definitions (D-06):** In the specific context of single-agent Claude Code execution, explicit role assignments add more overhead than value. We concede these should be informational context, not formal assignments.

3. **OQ-007 blocking status (D-04):** Opus is right that the approval gate mechanism (OQ-007) is blocking for contract infrastructure design. It determines how TodoWrite checkpoints interact with phase boundaries.

4. **Concrete `--dry-run` decision (D-13):** Opus's resolution (`--dry-run` = Phases 0-2, no codegen; `--skip-integration` = skip Phase 4) is reasonable and well-reasoned. Deferring this specific decision adds no value when the answer is relatively obvious from the spec.

### Variant B Remaining Disagreements

1. **Phase granularity:** 8 phases with single-responsibility boundaries is materially safer for 0.92 complexity. Opus's Phase 2 bundles three concerns and produces ambiguous failure signals.

2. **Contract framework timing:** Isolated contract testing (our Phase B) before any pipeline phase is an engineering best practice that Opus dismisses as "integration-testing fallacy" without engaging with the actual risk: debugging contract bugs in the presence of Phase 0/1 bugs.

3. **Timeline units:** Days are the standard planning unit across all project management frameworks. Session-based estimates are an accommodation to tooling, not a planning discipline.

4. **Negative testing as a coherent phase:** Distributing failure scenarios across milestones loses the conceptual unity of negative-path testing. Phase H as a dedicated validation phase is architecturally cleaner.

5. **Schema versioning (D-12):** Acknowledged by Opus as a gap, but adding it to a milestone isn't sufficient — it needs to be a prerequisite decision, not an implementation afterthought.

---

## Convergence Assessment

### Areas of Agreement (Strong Convergence)

1. **Ref file remediation first** — both agree RISK-002 is the highest priority and must be resolved before any pipeline work.
2. **Legacy directory deferred removal** — Variant B conceded; both now agree removal happens after full validation.
3. **Contract schema versioning needed** — Variant A conceded; both now agree this is a gap.
4. **Determinism specificity** — both agree on enumerating specific artifacts that must be deterministic.
5. **Broader negative fixtures** — both agree stale-ref, API-drift, and collision fixtures should exist.
6. **OQ-007 and OQ-008 both blocking** — resolved through mutual concession.
7. **Concrete `--dry-run` semantics** — Variant B conceded Opus's resolution is sound.
8. **Role definitions informational only** — Variant B conceded in single-agent context.
9. **All 18 shared assumptions** — fully aligned on foundational architecture.

### Areas of Persistent Disagreement (Requiring Resolution)

1. **Phase granularity (D-01):** 5 vs 8 phases. This is the highest-impact structural decision. Both positions have merit; the choice depends on whether coordination overhead (8 phases) or ambiguous failure isolation (5 phases) is the greater risk. **Recommendation:** Adopt Opus's 5-phase structure but add explicit sub-phase exit criteria matching Haiku's phase boundaries (B, C, D boundaries become milestone exit gates within Opus's Phase 2).

2. **Contract framework timing (D-03):** Bundled vs isolated. **Recommendation:** Compromise — implement contract *schemas* as a prerequisite (Haiku's instinct), but validate contract *behavior* through Phase 0 execution (Opus's instinct). This means: define schemas first, then prove them with real data.

3. **Timeline units (D-02):** Sessions vs days. **Recommendation:** Use days as the primary unit (for planning), with session counts as secondary (for execution tracking). The merged roadmap should provide both.

4. **Negative testing structure (D-09):** Distributed vs dedicated phase. **Recommendation:** Adopt Haiku's dedicated validation phase concept, but keep it as a milestone within Opus's Phase 5 structure rather than a standalone phase.

### Merge Priority

For the merged roadmap, prioritize:
- Opus's 5-phase structure with Haiku's milestone-level granularity within phases
- Haiku's determinism specificity and negative-fixture breadth
- Opus's concrete OQ resolutions and legacy removal timing
- Haiku's day-based timeline with session annotations
- Haiku's schema versioning as a prerequisite
- Opus's MCP degradation testing as a dedicated milestone
