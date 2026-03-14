---
convergence_score: 0.72
rounds_completed: 2
---

# Adversarial Debate: Opus-Architect (A) vs Haiku-Architect (B)

## Divergence Points Under Debate

From the diff analysis, 14 divergence points were identified. This debate focuses on the 5 most consequential ones where genuine architectural tension exists:

1. Phase 0 necessity (D-1)
2. Infrastructure parallelization vs sequencing (D-3/D-4)
3. Validation approach: matrix vs layers (D-8)
4. Timeline format: qualitative vs quantitative (D-9)
5. Signal vocabulary resolution timing (D-5)

---

## Round 1: Initial Positions

### D-1: Phase 0 Architecture Confirmation

**Variant A (Opus)**: Phase 0 is unnecessary overhead. The spec is already detailed enough to begin implementation. Open questions are documented in Section 7 with blocking annotations per phase. Developers resolve them just-in-time as they reach the relevant phase. Adding a dedicated pre-coding phase introduces calendar delay (0.5-1 day) for what amounts to a meeting and a decision document. The roadmap already identifies which questions block which phases -- that's sufficient. Starting Phase 1 (pure programmatic foundation) while ambiguities exist in Phase 4 (convergence) is perfectly safe because those concerns are 2-3 phases away.

**Variant B (Haiku)**: Phase 0 is essential risk management, not overhead. The spec contains at least 3 blocking ambiguities: timeout semantics for convergence iterations, resume behavior for partial `synthesize-spec`, and scoring precision vs downstream gate boundary handling. These are not isolated to late phases -- they affect domain model design in Phase 1. For example, `PortifyConfig` must include timeout settings, and `PortifyStepResult` must carry resume metadata. If timeout semantics are unresolved, the config model is speculative. Phase 0 costs 0.5-1 day but prevents 2-3 days of rework when Phase 4 forces model changes that ripple back to Phase 1. Front-loading decisions has asymmetric payoff.

### D-3/D-4: Infrastructure Parallelization vs Sequencing

**Variant A (Opus)**: Phase 5 (Infrastructure) can and should run in parallel with Phase 2 onward. Monitor, logging, contract emission, and diagnostics have no data dependency on Claude-assisted outputs. The critical path diagram shows this clearly: the main pipeline is Phase 1 -> 2 -> 3 -> 4, while infrastructure forks off Phase 1 and merges back before final integration. This parallelism is the single largest opportunity to reduce wall-clock time. Sequential execution is already identified as risk R-8. Refusing to parallelize infrastructure when it's architecturally independent is leaving delivery speed on the table for no safety gain.

**Variant B (Haiku)**: Subprocess infrastructure must be stable *before* content steps depend on it. Opus's parallelization assumes infrastructure and content are truly independent, but they're not. `PortifyProcess`, monitoring, and gate engine bindings are used by *every* Claude-assisted step. If you build Steps 3-4 (analyze-workflow, design-pipeline) concurrently with the subprocess platform, you're coding against an unstable API. Phase 3 (subprocess orchestration core) should be a prerequisite gate -- build it, test it, then let content steps rely on it. The sequencing adds maybe 2-3 days to calendar time but eliminates integration risk entirely. For a first implementation, safety over speed is the correct trade-off.

### D-8: Validation Approach

**Variant A (Opus)**: The SC-001 through SC-014 automated validation matrix provides direct traceability from success criteria to test type to validation method. Every criterion has a clear, auditable test. This is how you prove compliance: a table where each row is a requirement, and each column tells you how it's verified. Layer-based organization (unit -> integration -> compliance) is fine for test execution order, but it doesn't answer "how do I know SC-007 is validated?" You need the matrix for that.

**Variant B (Haiku)**: Layer-based test organization reflects how tests are actually written, executed, and maintained. Unit tests run first and fast, integration tests exercise orchestration, compliance checks are static analysis, and architectural validation ensures invariants. The evidence package concept ties it together: test results, artifact samples, git diff proofs, and boundary test evidence form a releasable bundle. A validation matrix is useful as an index, but organizing tests by layer is how you structure a test suite. The matrix is a view, not an architecture.

### D-9: Timeline Format

**Variant A (Opus)**: Qualitative sizing (Small/Medium/Large) avoids false precision. Software estimation is notoriously unreliable, and specific day counts create expectations that become constraints. Saying "Phase 4 is Large" communicates relative effort without committing to "2-3 days" that could easily become 5. The team can calibrate S/M/L to their own velocity. Day counts in a roadmap become project management artifacts that get weaponized against implementers.

**Variant B (Haiku)**: Quantitative estimates (0.5-3 days per phase, 10.5-18 days total) with week-by-week cadence enable real planning. A roadmap without timeline is a wish list. Ranges acknowledge uncertainty (2-3 days, not 2.5 days). The 3-week cadence (foundation, content, validation) gives stakeholders a realistic picture. "Large" means nothing to someone allocating resources or coordinating dependencies. Day ranges with explicit buffer (Week 3) are honest and actionable. If the team finds them too aggressive, they recalibrate -- but they have a starting point.

### D-5: Signal Vocabulary Resolution Timing

**Variant A (Opus)**: GAP-008 (NDJSON signal vocabulary) is explicitly listed as a blocking open question for Phase 5. This is deliberate -- the vocabulary should be defined before implementation begins. Without knowing what signals the monitor extracts from Claude output, you can't build the monitor. Haiku assumes this will be resolved during implementation, which risks ad-hoc signal design, inconsistent event types, and monitor-subprocess coupling that's hard to refactor.

**Variant B (Haiku)**: Signal vocabulary emerges naturally from subprocess implementation. Phase 3 includes signal extraction as part of monitoring and diagnostics work. You can't fully define the vocabulary in isolation because you don't know what Claude's subprocess output looks like until you build the steps. A minimal starting vocabulary (start, complete, error, timeout) is sufficient to begin, and it grows as steps are implemented. Over-specifying signals upfront produces a vocabulary that doesn't match reality.

---

## Round 2: Rebuttals

### D-1: Phase 0 Architecture Confirmation

**Variant A rebuts B**: The claim that timeout semantics affect `PortifyConfig` in Phase 1 is overstated. Config can define a `timeout_seconds: int` field without knowing whether it applies per-iteration or total-divided-by-iterations. That's a *usage* decision, not a *type* decision. The config stores the value; the convergence loop interprets it. Similarly, resume metadata in `PortifyStepResult` can carry a generic `resume_context: dict` without knowing exact resume semantics. Phase 0 solves a coordination problem, not a technical one. If you're a single implementer (the common case for this project), you resolve ambiguities as you reach them.

**Variant B rebuts A**: A generic `timeout_seconds: int` without defined semantics is exactly the kind of speculative modeling that causes rework. When Phase 4 reveals that timeout must be per-iteration with a separate total budget cap, you need `iteration_timeout` AND `total_budget_timeout` -- two fields, not one. Resume metadata as `dict` is a type-safety abdication. Phase 0 isn't a meeting -- it's a decision record that takes 4 hours and prevents 2 days of refactoring. The "single implementer" argument makes Phase 0 *more* important, not less: a single person has no one to catch their assumptions until late integration.

### D-3/D-4: Infrastructure Parallelization vs Sequencing

**Variant A rebuts B**: The "unstable API" concern conflates two different things. `PortifyProcess` (the subprocess wrapper) extends `pipeline.ClaudeProcess`, which already has a stable API. The monitor and diagnostics consume subprocess output -- they don't change the subprocess interface. Content steps call `PortifyProcess.run()` and get results. That API is stable from day one because it inherits from a proven base class. What's parallelizable is the *consumer* side: monitor formatting, JSONL emission, TUI rendering, resume logic. These don't affect how Steps 3-7 invoke Claude.

**Variant B rebuts A**: `PortifyProcess` extends `ClaudeProcess`, yes, but the extension surface is the risk. `--add-dir` support, prompt construction with `@path` references, exit code capture, timeout state, and diagnostic collection -- these are *new* behaviors. Content steps depend on all of them. If you're building `analyze-workflow` while `PortifyProcess` is still having its `--add-dir` handling debugged, you're blocked or building against mocks that don't match the real behavior. Build the platform, stabilize it, then build on it. This is basic dependency management.

### D-8: Validation Approach

**Variant A rebuts B**: The evidence package is a good idea, but it's an output format, not a test organization principle. You can produce an evidence package from matrix-organized tests just as easily. The question is: when a gate fails in production, can you immediately identify which test validates that gate? SC-007 -> Integration -> "Mock convergence loop with known outputs" gives you that in one lookup. Layer-based organization requires you to search across the integration test suite to find convergence-related tests. Traceability is the primary concern for a gate-heavy system.

**Variant B rebuts A**: Traceability and organization aren't mutually exclusive. Use the SC matrix as a cross-reference index, but organize the actual test code by layers. This is standard practice -- requirements traceability matrices exist alongside test suites organized by execution characteristics. The matrix tells you *what* validates *what*; the layers tell you *how* and *when* tests run. Both are needed. This is a false dichotomy.

### D-9: Timeline Format

**Variant A rebuts B**: "A roadmap without timeline is a wish list" -- only if the audience is project managers. For implementers, the roadmap is a dependency graph with effort sizing. S/M/L conveys the same information as "1-2 days" / "2-3 days" / "3-5 days" without the illusion of precision. The 10.5-18 day range spans 70% -- that's not actionable for resource allocation. It's a range so wide it communicates the same thing as S/M/L with more digits.

**Variant B rebuts A**: The range communicates that this is a 2-3 week project, not a 1-week or 6-week project. That's valuable for planning. S/M/L doesn't tell you whether "Large" means 3 days or 3 weeks. The week-by-week cadence (Phase 0-3 in Week 1, Phase 4-6 in Week 2, Phase 7 + buffer in Week 3) creates natural checkpoints. If Week 1 deliverables slip, you know immediately. With S/M/L, there's no temporal reference frame for measuring progress. Ranges acknowledge uncertainty while still enabling planning.

### D-5: Signal Vocabulary Resolution Timing

**Variant A rebuts B**: "Emerges naturally" is another way of saying "ad-hoc." A minimal vocabulary (start, complete, error, timeout) is a vocabulary definition -- that's what Phase 0 or early Phase 5 should produce. The issue isn't defining every signal upfront; it's having *no* plan at all. Without an initial schema, each step's monitoring integration will invent its own signal names, and you'll spend integration time reconciling `step_begin` vs `step_start` vs `phase_started`.

**Variant B rebuts A**: Fair point on naming consistency. A minimal vocabulary defined early is reasonable. But blocking Phase 5 implementation on a comprehensive vocabulary (as Opus's "blocking open question" framing implies) is overkill. Define the minimal set (start, complete, error, timeout, gate_pass, gate_fail) in Phase 1 as constants, extend in Phase 3 when subprocess behavior is understood. This is Haiku's approach with a slightly earlier definition point.

---

## Convergence Assessment

### Areas of Agreement Reached

1. **Phase 0 scope** (Partial convergence): Both sides acknowledge that *some* upfront decision-making is needed. The dispute is whether it warrants a named phase or can be handled via the existing open-questions list. **Resolution tendency**: A lightweight Phase 0 (half-day decision record) is the pragmatic middle ground. Both sides implicitly accept this.

2. **Validation approach** (Strong convergence): Round 2 revealed this is a false dichotomy. Use the SC matrix as a traceability index, organize test code by layers. Both approaches are complementary, not competing. **Agreed**: Merge both -- SC matrix for traceability, layers for test organization, evidence package for release readiness.

3. **Signal vocabulary** (Strong convergence): Both sides converged on "define a minimal vocabulary early, extend during implementation." The disagreement was about *how early* and *how minimal*, not whether to define one. **Agreed**: Define minimal constants in Phase 1, extend in Phase 3.

4. **Timeline format** (Partial convergence): Variant B's week-by-week cadence provides planning utility that S/M/L doesn't. Variant A's concern about false precision is valid for day-level estimates. **Resolution tendency**: Use Haiku's quantitative ranges with Opus's qualitative sizing as cross-checks, per the diff analysis recommendation.

### Remaining Disputes

1. **Infrastructure parallelization vs sequencing** (D-3/D-4): This remains the sharpest disagreement. Opus argues that `PortifyProcess` inherits a stable API and infrastructure consumers are parallelizable. Haiku argues that the extension surface is the risk and building on an unstabilized platform creates hidden integration costs. **Unresolved**: Both positions are defensible. The diff analysis recommendation (sequence for first implementation, parallelize in future releases) slightly favors Haiku but neither side conceded.

2. **Phase 0 as named phase vs inline resolution** (D-1): Variant A accepts the need for upfront decisions but resists dedicating a named phase to them. Variant B insists the named phase creates accountability and a decision record. **Unresolved**: This is partly a process/culture question, not purely technical.

### Scoring Rationale

**Convergence score: 0.72** -- Strong convergence on 3 of 5 debated points (validation, signal vocabulary, timeline format). Partial convergence on Phase 0. Genuine unresolved disagreement on infrastructure parallelization. The 12 shared assumptions from the diff analysis (not debated) further anchor overall alignment. The remaining disputes are real but bounded in scope and impact.
